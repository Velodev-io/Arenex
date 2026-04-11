# Startup + CORS Spec

## Overview
Two tasks in this spec:
1. A `start.sh` bash script that starts both game agents with a single command.
2. A CORS fix that must be applied to **both** agents so the browser can call them.

---

## Task 1: `start.sh`

### What It Does
Shell script placed at `platform/start.sh`. Starts both agents in the background and prints a ready message.

### Script Content
```bash
#!/bin/bash

# Start Tic-Tac-Toe agent on port 8000
uvicorn agents.tictactoe.agent:app --host 0.0.0.0 --port 8000 &
TTT_PID=$!
echo "Tic-Tac-Toe agent started (PID $TTT_PID) on port 8000"

# Start Chess agent on port 8001
uvicorn agents.chess.agent:app --host 0.0.0.0 --port 8001 &
CHESS_PID=$!
echo "Chess agent started (PID $CHESS_PID) on port 8001"

echo ""
echo "Platform ready — open platform/frontend/index.html in your browser."
echo "Press Ctrl+C to stop both agents."

# Wait for any process to exit
wait
```

### How to Run
```bash
chmod +x platform/start.sh
./platform/start.sh
```

### Placement
```
platform/
├── start.sh
├── frontend/
│   ├── index.html
│   ├── tictactoe.html
│   └── chess.html
└── agents/
    ├── tictactoe/
    │   └── agent.py
    └── chess/
        └── agent.py
```

---

## Task 2: CORS Middleware Fix

### Why It's Required
Web browsers block `fetch()` calls to a different origin (e.g., from `file://` or `localhost:3000` to `localhost:8000`). Adding CORS middleware allows the browser-based frontend to reach the locally running agents.

### What to Add to BOTH Agents
Add the following immediately after `app = FastAPI(...)` in **both** `agents/tictactoe/agent.py` and `agents/chess/agent.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### How to Verify It Works
After starting both agents, run in a browser console:
```javascript
fetch("http://localhost:8000/health").then(r => r.json()).then(console.log)
fetch("http://localhost:8001/health").then(r => r.json()).then(console.log)
```
Both should return `{ status: "ok", agent: "..." }` without CORS errors.
