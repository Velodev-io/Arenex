# Orchestrator Spec

## Overview
This script oversees the end-to-end self-improvement pipeline of the Chess Agent. It acts as the glue that ties the Builder Agent, the FastAPI Server, and the Tester Agent together into an automated feedback loop. This is Phase 4 of the architecture.

## Dependencies
- `subprocess`, `signal`, `os`, `sys`, `time` (standard Python libraries for process management)
- `argparse` (CLI parsing)
- `builder_agent` and `tester_agent` (local imports)

## Core Logic and Flow

The orchestrator operates in a `while` loop up to a configurable maximum number of iterations.

For each iteration:
1.  **Build Phase:** Programmatically calls the `run()` function in `builder_agent.py`. It passes the path to the `tester_report.json` if one exists from a previous iteration. Wait for generation to complete and write `chess_agent.py` to disk.
2.  **Server Startup Phase:** Spawns a background subprocess running `python chess_agent.py`.
    *   Sleeps for a short duration (`~3.0s`) to allow `uvicorn` to initialize.
    *   Checks the process status. If it crashed immediately, halts the pipeline.
3.  **Test Phase:** Programmatically calls the `run()` function in `tester_agent.py`, directing it at the newly launched local server (`http://localhost:8001`). Waits for the tests to complete and return a report dictionary.
4.  **Server Teardown Phase:** Closes the FastAPI server to free up port `8001` for the next iteration.
    *   Sends a graceful `SIGTERM` signal.
    *   Waits up to 5 seconds.
    *   Falls back to a hard `SIGKILL` if the process hangs.
5.  **Evaluation Phase:** Reads the `pass_rate` and boolean `passed` flag from the test report.
    *   **If Passed:** Prints a success banner and halts the pipeline cleanly. The `chess_agent.py` file on disk represents the final, passed state.
    *   **If Failed:** Prints the identified weaknesses, assigns the `tester_report.json` output path as the input for the next iteration, and restarts the loop.

## Termination Conditions
The loop terminates under three specific conditions:
1.  **Success:** The `pass_rate` from the Tester Agent equals or exceeds the configured threshold.
2.  **Max Iterations:** The loop attempts to build and test `<max_iterations>` times but never reaches the success threshold.
3.  **Fatal Errors:** The Builder Agent crashes (e.g. Anthropic API down), or the server fundamentally fails to launch.

## How to Run

Execute the pipeline with default configuration (5 iterations max, 80% passing threshold):
```bash
python orchestrator.py
```

Override defaults using CLI arguments:
```bash
python orchestrator.py --max-iterations 10 --threshold 0.95
```
