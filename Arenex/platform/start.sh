#!/bin/bash

# Ensure we're running from the platform directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Starting Arenex Games Platform..."

# Start Tic-Tac-Toe agent on port 8010
uvicorn agents.tictactoe.agent:app --host 0.0.0.0 --port 8010 &
TTT_PID=$!
echo "Tic-Tac-Toe agent started (PID $TTT_PID) on port 8010"

# Start Chess agent on port 8011
uvicorn agents.chess.agent:app --host 0.0.0.0 --port 8011 &
CHESS_PID=$!
echo "Chess agent started (PID $CHESS_PID) on port 8011"

echo ""
echo "========================================================"
echo "Platform ready!"
echo "Open the following file in your browser to play:"
echo "$DIR/frontend/index.html"
echo "========================================================"
echo ""
echo "Press Ctrl+C to stop both agents."

# Wait for any process to exit (or for user interrupt)
wait
