# Maia-1100 Chess Agent

A human-like chess agent that uses the **Maia-1100** neural network weights. Unlike traditional engines (like Stockfish), Maia was trained on millions of games by human players to predict their moves, making it an excellent practice partner for players around 1100 Elo.

## 🏗 Architecture

- **Core Engine**: `lc0` (Leela Chess Zero)
- **Weights**: `maia-1100.pb.gz`
- **Inference Strategy**: `nodes 1` (pure neural network prediction, no search tree exploration)
- **Backend API**: FastAPI (Python)

## 🛠 Dependencies

1. **System**: `lc0` (installed via `brew install lc0`)
2. **Python**:
   - `fastapi`
   - `uvicorn`
   - `python-chess`
   - `httpx`

## 🚀 Running the Agent

1. **Install lc0**:
   ```bash
   brew install lc0
   ```

2. **Start the Agent Server**:
   ```bash
   cd agents/maia1100
   source ../../.venv/bin/activate
   pip install -r requirements.txt
   python3 agent.py
   ```
   The agent runs on port **8002**.

## 🔌 API Contract

### POST `/move`
Processes a move request.
- **Request**:
  ```json
  {
    "board": "FEN_STRING",
    "your_color": "white"
  }
  ```
- **Response**:
  ```json
  {
    "move": "e2e4",
    "reasoning": "Maia-1100 prediction (nodes 1)"
  }
  ```

## ⚙️ UCI Communication Pattern

The agent communicates with `lc0` via a persistent subprocess using the UCI protocol. 
Upon startup, it initializes the engine with Metal acceleration:
1. `uci`
2. `setoption name Threads value 2`
3. `isready`

For move generation:
1. `position fen <FEN>`
2. `go nodes 1`
3. Parses the `bestmove` token from the standard output.
