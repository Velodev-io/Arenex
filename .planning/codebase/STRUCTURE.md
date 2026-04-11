# Project Structure - Arenex

**Analysis Date:** 2026-04-11

## Directory Layout

```text
Arenex/
├── platform/                      # Production gaming platform
│   ├── frontend/                 # Web UI assets
│   │   ├── index.html            # Entry point / Game selector
│   │   ├── chess.html            # Chess UI
│   │   └── tictactoe.html        # Tic-Tac-Toe UI
│   ├── agents/                   # Deployed FastAPI game servers
│   │   ├── chess/                # Chess agent logic
│   │   └── tictactoe/            # TTT agent logic
│   └── start.sh                  # Orchestration script
│
├── ChessAgent/                    # Research & Development Lab (Chess)
│   ├── chess_builder.py          # Auto-heuristic generator
│   ├── chess_tester.py           # Benchmarking logic
│   ├── chess_orchestrator.py     # Batch testing
│   └── requirements.txt          # Lab-specific dependencies
│
├── Tic-Tac-ToeAgent/              # Original TTT prototype
│   └── agent.py                  # Prototype TTT AI
│
├── agents/                        # Project Metadata and Logic docs
│   ├── platform/                 # Agent system prompts/contracts
│   ├── chess/                    # Chess-specific logic specs
│   └── tictactoe/                # TTT-specific logic specs
│
├── .agent/                        # GSD Skill/System directory
└── requirements.txt               # Main platform dependencies
```

## Key File Locations

- **Main Startup:** `platform/start.sh`
- **Main Entry:** `platform/frontend/index.html`
- **Chess Brain:** `platform/agents/chess/agent.py`
- **TTT Brain:** `platform/agents/tictactoe/agent.py`

---
*Structure analysis: 2026-04-11*
