import os
import sys

def parse_env(file_path):
    keys = set()
    if not os.path.exists(file_path):
        return keys
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                keys.add(line.split('=')[0].strip())
    return keys

def main():
    root = os.getcwd()
    env_path = os.path.join(root, '.env')
    example_path = os.path.join(root, '.env.example')

    if not os.path.exists(env_path):
        # No .env to check against, that's fine
        return

    env_keys = parse_env(env_path)
    example_keys = parse_env(example_path)

    missing = env_keys - example_keys
    if missing:
        print(f"WARNING: The following keys are in .env but missing from .env.example: {', '.join(missing)}")
        print("Please update .env.example to match .env structure.")
        # We don't block the commit per requirement: "Warn (don't block) if .env.example is missing a key"
    else:
        print(".env.example is up to date with .env keys.")

if __name__ == "__main__":
    main()
