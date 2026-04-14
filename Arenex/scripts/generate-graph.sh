#!/bin/bash
# Helper script to run graphify using the security_venv and pointing to the .venv libraries
# This bypasses the Python version conflict (dataclass slots) by using Python 3.9 + networkx 2.8.8.

export PYTHONPATH=$(pwd)/.venv/lib/python3.14/site-packages
AGENT_PYTHON=$(pwd)/security_venv/bin/python3

if [ ! -d "security_venv" ]; then
    echo "Error: security_venv not found. Run patch first."
    exit 1
fi

$AGENT_PYTHON -m graphify "$@"
