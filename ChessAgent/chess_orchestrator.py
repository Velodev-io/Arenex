"""
chess_orchestrator.py
---------------------
Oversees the end-to-end self-improvement pipeline of the Chess Agent.
Calls the builder, starts the server, runs the tester, and loops based
on pass rate telemetry.

Implemented from spec: agents/chess/orchestrator.md
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from typing import Optional

# Local imports following our naming conventions
import chess_builder

# The tester will be named chess_tester.py, we assume it has a run() method.
try:
    import chess_tester
except ImportError:
    chess_tester = None  # Will be implemented in the next step

# Constants
SERVER_SCRIPT = "chess_ai_server.py"
SERVER_URL = "http://localhost:8001"
REPORT_PATH = "tester_report.json"
STARTUP_WAIT_SEC = 3.0

def start_server() -> subprocess.Popen:
    """Spawns the chess agent server in the background and waits for init."""
    print(f"Starting server: {SERVER_SCRIPT}...")

    # Needs to be in the same directory, run using the current python executable
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for Uvicorn to start
    time.sleep(STARTUP_WAIT_SEC)

    if proc.poll() is not None: # Process exited early
        out, err = proc.communicate()
        print(f"Error: Server failed to start immediately.\nSTDOUT: {out.decode()}\nSTDERR: {err.decode()}", file=sys.stderr)
        sys.exit(1)

    print(f"Server successfully started with PID {proc.pid}.")
    return proc

def stop_server(proc: subprocess.Popen):
    """Gracefully terminates the given subprocess with a SIGKILL fallback."""
    if not proc or proc.poll() is not None:
        return

    print(f"Shutting down server (PID {proc.pid})...")
    try:
        os.kill(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5.0)
        print("Server shutdown completed smoothly.")
    except subprocess.TimeoutExpired:
        print("Server shutdown timed out. Forcing SIGKILL...")
        proc.kill()
        proc.wait()
    except ProcessLookupError:
        pass # Process already gone

def run_pipeline(max_iterations: int = 5, threshold: float = 0.8):
    if not chess_tester:
        print("Error: chess_tester.py is not yet implemented. Cannot run Orchestrator.", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(" ARENEX CHESS AGENT ORCHESTRATOR")
    print("=" * 60)
    print(f"Max expected iterations: {max_iterations}")
    print(f"Success threshold: {threshold*100:.1f}%")

    report_path: Optional[str] = None

    for iteration in range(1, max_iterations + 1):
        print("\n" + "-" * 60)
        print(f" ITERATION {iteration} OF {max_iterations}")
        print("-" * 60)

        server_proc = None
        try:
            # 1. Build Phase: Generates chess_ai_server.py
            print("\n[Phase 1] Building Chess Agent...")
            try:
                code = chess_builder.generate_chess_agent(report_path)
                with open(SERVER_SCRIPT, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception as e:
                print(f"Fatal Error during build phase: {e}", file=sys.stderr)
                sys.exit(1)

            # 2. Server Startup Phase
            print("\n[Phase 2] Starting Server...")
            server_proc = start_server()

            # 3. Test Phase
            print("\n[Phase 3] Running Tester Agent...")
            # We assume chess_tester.run() executes the suites and returns a report dictionary.
            # It should also write to REPORT_PATH locally.
            report = chess_tester.run(agent_url=SERVER_URL, output_path=REPORT_PATH)

        finally:
            # 4. Server Teardown Phase
            print("\n[Phase 4] Server Teardown...")
            if server_proc:
                stop_server(server_proc)

        # 5. Evaluation Phase
        pass_rate = report.get("pass_rate", 0.0)
        passed = report.get("passed", False)

        print("\n[Eval] Evaluation complete:")
        print(f"  > Pass Rate: {pass_rate*100:.1f}%")

        if passed or pass_rate >= threshold:
            print("\n" + "=" * 60)
            print(" ✓ PIPELINE SUCCESS: QUALITY THRESHOLD MET")
            print("=" * 60)
            print(f"Final pass rate: {pass_rate*100:.1f}%")
            print(f"The optimized {SERVER_SCRIPT} is ready.")
            break

        else:
            print("  > Threshold not met. Identified Weaknesses:")
            for w in report.get("identified_weaknesses", []):
                print(f"    - {w}")

            report_path = REPORT_PATH
            if iteration == max_iterations:
                print("\n" + "=" * 60)
                print(" ✗ PIPELINE HALTED: MAX ITERATIONS REACHED")
                print("=" * 60)
                print(f"Final pass rate: {pass_rate*100:.1f}% vs threshold {threshold*100:.1f}%")
            else:
                print("\nLooping back to Builder Phase with feedback report...")
                time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-end self-improvement pipeline orchestrator.")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum loop iterations")
    parser.add_argument("--threshold", type=float, default=0.8, help="Pass rate threshold")

    args = parser.parse_args()

    run_pipeline(max_iterations=args.max_iterations, threshold=args.threshold)
