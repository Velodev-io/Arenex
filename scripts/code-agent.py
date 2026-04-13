import os
import re
import sys
import json
import ast
import argparse
import subprocess
from datetime import datetime
try:
    from git import Repo
except ImportError:
    Repo = None
from rich.console import Console
from rich.table import Table

console = Console()

# --- Configuration ---
BLACKLIST_DIRS = {'.venv', 'node_modules', 'graphify-out', '.git', '__pycache__', 'migrations', 'security_venv'}
BLACKLIST_FILES = {'package-lock.json', 'code-agent-report.md', 'code-agent.py', 'bandit-out.json'}
ALLOWED_FIX_TYPES = {
    'var_to_const', 
    'on_to_once', 
    'print_to_logging', 
    'raw_action_to_constant', 
    'secret_to_env',
    'is_none',
    'except_pass'
}

# Regex Patterns
RE_SECRETS = {
    'hardcoded_api_key': r'(sk-|pk_live_|rk_live_|AIza|ghp_|ghs_)[a-zA-Z0-9]{5,}',
    'database_url': r'(postgres|postgresql|neon)://[a-zA-Z0-9]+:[a-zA-Z0-9]+@',
    'jwt_secret': r'(JWT_SECRET|SECRET_KEY)\s*=\s*["\'][^"\']{5,}["\']',
    'razorpay_key': r'rzp_(live|test)_[a-zA-Z0-9]{5,}',
    'redis_password': r'redis://:[a-zA-Z0-9]+@',
    'generic_secret': r'(password|secret|token|api_key)\s*=\s*["\'](?!env:)[^"\']{3,}["\']'
}

class CodeAgent:
    def __init__(self, mode='scan', target_path='.'):
        self.mode = mode
        self.target_path = target_path
        self.issues = []
        self.fixed_count = 0
        self.repo = None
        if Repo:
            try:
                self.repo = Repo('.')
            except:
                pass

    def check_git_status(self):
        if self.mode == 'fix' and self.target_path == '.' and self.repo and self.repo.is_dirty():
            console.print("[bold red]ERROR: Uncommitted changes detected. Commit or stash before running --fix mode.[/bold red]")
            sys.exit(1)

    def get_files_to_scan(self):
        files = []
        for root, dirs, filenames in os.walk(self.target_path):
            dirs[:] = [d for d in dirs if d not in BLACKLIST_DIRS]
            for f in filenames:
                if f in BLACKLIST_FILES or f.endswith('.pyc'):
                    continue
                if f.endswith(('.py', '.js', '.json')) or f.startswith('.env'):
                    files.append(os.path.join(root, f))
        return files

    def _add_issue(self, issue_type, severity, file, line, desc, snippet, fix_suggestion, fix_type=None):
        self.issues.append({
            "type": issue_type, "severity": severity, "file": file, "line": line,
            "issue": desc, "code_snippet": snippet, "fix": fix_suggestion,
            "fix_type": fix_type, "auto_fixed": False
        })

    def scan_file(self, file_path):
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()

            self._scan_secrets(file_path, lines)
            self._scan_dangerous_files(file_path)

            if file_path.endswith('.py'):
                self._scan_python(file_path, content, lines)
            elif file_path.endswith('.js'):
                self._scan_javascript(file_path, content, lines)
        except Exception as e:
            console.print(f"[yellow]Skipping {file_path}: {e}[/yellow]")

    def _scan_secrets(self, file_path, lines):
        for i, line in enumerate(lines):
            for name, pattern in RE_SECRETS.items():
                if re.search(pattern, line):
                    self._add_issue("secret", "critical", file_path, i+1, f"Hardcoded {name}", line.strip(), "Move to env", "secret_to_env")

    def _scan_dangerous_files(self, file_path):
        fname = os.path.basename(file_path)
        if fname == '.env':
            self._add_issue("dangerous_file", "critical", file_path, 0, ".env file tracked by git", "File detected", "Add to .gitignore")
        if file_path.endswith(('.pem', '.key', '.p12')):
            self._add_issue("dangerous_file", "critical", file_path, 0, "Security certificate detected", "Cert extension", "Remove from repo")
        if os.path.getsize(file_path) > 1024 * 1024:
            self._add_issue("quality", "low", file_path, 0, "File too large (>1MB)", "Large file", "Move to LFS")

    def _scan_python(self, file_path, content, lines):
        try:
            v_res = subprocess.run(['security_venv/bin/vulture', file_path, '--min-confidence', '100'], capture_output=True, text=True)
            for line in v_res.stdout.splitlines():
                if 'unused' in line:
                    m = re.search(r':(\d+):', line)
                    l_num = int(m.group(1)) if m else 0
                    self._add_issue("quality", "low", file_path, l_num, "Unused import/code", line, "Remove unused node", None)
        except: pass

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg in node.args.defaults:
                        if isinstance(arg, (ast.List, ast.Dict)):
                            self._add_issue("bug", "high", file_path, node.lineno, "Mutable default argument", f"def {node.name}(...)", "Use None as default", None)
                
                if isinstance(node, ast.Try):
                    for handler in node.handlers:
                        if handler.type and isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                            if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                                self._add_issue("bug", "high", file_path, handler.body[0].lineno, "Silent exception swallow", "except Exception: pass", "Add logging", "except_pass")
        except: pass

        for i, line in enumerate(lines):
            if 'print(' in line:
                self._add_issue("quality", "low", file_path, i+1, "print() instead of logging", line.strip(), "Use logger", "print_to_logging")
            if 'shell=True' in line:
                self._add_issue("security", "high", file_path, i+1, "Insecure subprocess call", line.strip(), "shell=False", None)
            if '== None' in line:
                self._add_issue("quality", "low", file_path, i+1, "Comparison to None", line.strip(), "is None", "is_none")

    def _scan_javascript(self, file_path, content, lines):
        for i, line in enumerate(lines):
            if "bot.on('spawn'" in line:
                self._add_issue("bug", "high", file_path, i+1, "Double-spawn bug", line.strip(), "bot.once", "on_to_once")
            if "var " in line:
                self._add_issue("quality", "low", file_path, i+1, "var keyword usage", line.strip(), "const/let", "var_to_const")
            if 'currentAction =' in line and "'" in line:
                self._add_issue("quality", "medium", file_path, i+1, "Raw action string", line.strip(), "Use ACTIONS", "raw_action_to_constant")

    def run_bandit(self):
        try:
            subprocess.run(['security_venv/bin/bandit', '-r', self.target_path, '-f', 'json', '-o', 'bandit-out.json', '--exclude', 'security_venv,node_modules,scripts/test-bait'], capture_output=True)
            if os.path.exists('bandit-out.json'):
                with open('bandit-out.json', 'r') as f:
                    for obj in json.load(f).get('results', []):
                        self._add_issue("security", obj['issue_severity'].lower(), obj['filename'], obj['line_number'], obj['issue_text'], obj['code'].strip(), "Secure pattern", None)
                os.remove('bandit-out.json')
        except: pass

    def apply_fixes(self):
        if self.mode != 'fix': return
        fixable = [i for i in self.issues if i['fix_type'] in ALLOWED_FIX_TYPES]
        if not fixable: return
        
        if self.repo and self.target_path == '.':
            branch = f"code-agent/fix-{datetime.now().strftime('%H%M%S')}"
            self.repo.git.checkout('-b', branch)
            console.print(f"[green]Fixes applied on branch {branch}[/green]")
        
        for file in set(i['file'] for i in fixable):
            with open(file, 'r') as f: lines = f.readlines()
            changed = False
            for iss in [i for i in fixable if i['file'] == file]:
                idx = iss['line'] - 1
                if idx < 0: continue
                old = lines[idx]
                if iss['fix_type'] == 'on_to_once': lines[idx] = lines[idx].replace("on('spawn'", "once('spawn'")
                elif iss['fix_type'] == 'var_to_const': lines[idx] = lines[idx].replace("var ", "const ")
                elif iss['fix_type'] == 'print_to_logging': lines[idx] = lines[idx].replace("print(", "logger.info(")
                elif iss['fix_type'] == 'is_none': lines[idx] = lines[idx].replace("== None", "is None")
                elif iss['fix_type'] == 'except_pass': lines[idx] = lines[idx].replace("pass", "logger.error(e)")
                elif iss['fix_type'] == 'raw_action_to_constant':
                    m = re.search(r"currentAction = '([^']+)'", lines[idx])
                    if m: lines[idx] = lines[idx].replace(f"'{m.group(1)}'", f"ACTIONS.{m.group(1).upper().replace(' ', '_')}")
                if lines[idx] != old:
                    iss['auto_fixed'] = True
                    self.fixed_count += 1
                    changed = True
            if changed:
                with open(file, 'w') as f: f.writelines(lines)
        if not (self.repo and self.target_path == '.'):
             console.print(f"[green]Applied {self.fixed_count} fixes locally.[/green]")

    def generate_report(self):
        with open("code-agent-report.md", 'w') as f:
            f.write("# Code Agent Report\n\n")
            for sev in ['critical', 'high', 'medium', 'low']:
                subset = [i for i in self.issues if i['severity'] == sev]
                if not subset: continue
                f.write(f"## {sev.upper()} Issues\n")
                for i in subset:
                    f.write(f"### {i['issue']} ({'Fixed' if i['auto_fixed'] else 'Manual'})\n- {i['file']}:{i['line']}\n- `{i['code_snippet']}`\n- Fix: {i['fix']}\n\n")
            f.write("## Manual Review Required\n")
            for i in [i for i in self.issues if not i['auto_fixed']]:
                f.write(f"- {i['file']}:{i['line']}: {i['issue']}. Fix: {i['fix']}\n")
        return "code-agent-report.md"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--path", default=".")
    args = parser.parse_args()

    agent = CodeAgent(mode='fix' if args.fix else 'scan', target_path=args.path)
    agent.check_git_status()
    for f in agent.get_files_to_scan(): agent.scan_file(f)
    agent.run_bandit()
    if args.fix: agent.apply_fixes()
    agent.generate_report()
    
    table = Table(title="Arenex Code Agent Results")
    for s in ['critical', 'high', 'medium', 'low']:
        table.add_row(s.upper(), str(len([i for i in agent.issues if i['severity'] == s])))
    console.print(table)
    console.print(f"Fixed: {agent.fixed_count} | Manual: {len([i for i in agent.issues if not i['auto_fixed']])}")

if __name__ == "__main__":
    main()
