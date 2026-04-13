#!/bin/bash
# Manual Security Audit Script for Arenex

echo "Starting Manual Security Audit..."
echo "=================================="

# Use the security virtualenv if it exists
if [ -d "security_venv" ]; then
    export PATH="$(pwd)/security_venv/bin:$PATH"
fi

# 1. Run pre-commit checks on all files
echo "Running pre-commit hooks on all files..."
pre-commit run --all-files

# 2. Additional manual checks
echo ""
echo "Running project-specific manual checks..."

echo "[Node.js Audit]"
cd minecraft-agent-template && npm audit --audit-level=high && cd ..

echo ""
echo "[Python Bandit Scan]"
bandit -r app/ -ll

echo ""
echo "[Python Dependency Audit]"
pip-audit -r requirements.txt

echo ""
echo "Security Audit Complete."
