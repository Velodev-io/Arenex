"""
chess_builder.py
----------------
This script continuously authors and improves the chess AI FastAPI server.
It uses the Groq API (e.g., Llama 3) to generate Python code based on a system prompt
and an optional tester failure report.

Implemented from spec: agents/chess/builder_agent.md
"""

import argparse
import json
import os
import re
import sys
from groq import Groq

# Output file name for the generated Chess AI
OUTPUT_FILE = "chess_ai_server.py"

SYSTEM_PROMPT = """You are an expert Python developer specializing in chess AI and the FastAPI framework.
Your job is to write or improve a chess agent that runs as a FastAPI server.

=== ARENEX AGENT REST CONTRACT ===
The server MUST implement these two endpoints exactly:

POST /move
  Input JSON:
    {
      "board": "<FEN string>",
      "your_color": "white" | "black",
      "game_id": "<string>"
    }
  Output JSON:
    {
      "move": "<UCI string>",
      "reasoning": "<string>"
    }

GET /health
  Output JSON:
    { "status": "ok", "agent": "chess-agent" }

=== MANDATORY LIBRARY ===
You MUST use the `python-chess` library for ALL of the following:
  - Parsing FEN strings:        chess.Board(fen)
  - Generating legal moves:     board.legal_moves
  - Detecting check:            board.is_check()
  - Detecting checkmate:        board.is_checkmate()
  - Making/unmaking moves:      board.push(move) / board.pop()
  - UCI move format:            move.uci()
  - Piece access:               board.piece_at(square)

DO NOT hand-roll move validation or check detection. python-chess handles all of it correctly.

=== PIECE VALUES ===
Use these values for material evaluation:
  Pawn = 1, Knight = 3, Bishop = 3, Rook = 5, Queen = 9, King = 1000

=== MOVE SELECTION PRIORITY LADDER ===
Implement choose_move(board: chess.Board) using this EXACT priority order. The first condition met dictatates the move.

  Priority 1: Don't move into check (Note: legal_moves inherently guarantees this)
  Priority 2: Checkmate opponent if possible (Simulate legal moves, check board.is_checkmate()) -> Reasoning: "Checkmate in one"
  Priority 3: Check opponent (if it leads to a winning position safely) -> Reasoning: "Delivering check to gain tempo"
  Priority 4: Capture the highest-value piece safely (highest positive net gain) -> Reasoning: "Capturing {piece_type} for material gain (+{net_gain})"
  Priority 5: Protect own pieces under attack (Move highest-value attacked piece to safety) -> Reasoning: "Protecting {piece_type} from capture"
  Priority 6: Control center squares (Place piece safely on e4, d4, e5, d5) -> Reasoning: "Controlling center square {square}"
  Priority 7: Develop pieces early (Move count < 10, prefer knights/bishops over queens/rooks) -> Reasoning: "Developing {piece_type} in the opening"
  Priority 8: Castle if possible (If castling rights exist and is a legal move) -> Reasoning: "Castling for king safety"
  Priority 9: Avoid moving the same piece twice in the opening (Track moved pieces if move count < 10) -> Reasoning: "Preferring undeveloped piece"
  Priority 10: Fall back to a random legal move -> Reasoning: "No strong heuristic applies, choosing randomly"

=== CODE REQUIREMENTS ===
1. The file must be a complete, runnable FastAPI application.
2. It must import chess, fastapi, pydantic, uvicorn.
3. Run on port 8001: `uvicorn.run(app, host="0.0.0.0", port=8001)`
4. The reasoning field MUST explain which priority fired and why.
5. All move validation goes through python-chess. NEVER hard-code square indices.
6. Return HTTP 400 Bad Request for edge cases (invalid FEN, game over, wrong side to move).
7. `choose_move()` must be pure (no side effects on the passed board, always push/pop cleanly).

=== OUTPUT FORMAT ===
Return ONLY the Python source code, wrapped in a single ```python ... ``` block. No conversational text.
"""

def generate_chess_agent(report_path: str = None) -> str:
    # 1. Environment Check
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Prompt Construction
    user_prompt = "Generate the complete chess AI server file from scratch implementing all 10 priorities."
    
    if report_path:
        if not os.path.exists(report_path):
            print(f"Error: Report file {report_path} not found.", file=sys.stderr)
            sys.exit(1)
            
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            
        user_prompt = (
            f"The previous version of the chess agent failed fully executing the tests.\n\n"
            f"Pass Rate: {report_data.get('pass_rate', 'N/A')}\n\n"
            f"Identified Weaknesses:\n"
            + "\n".join([f"- {w}" for w in report_data.get('identified_weaknesses', [])]) + "\n\n"
            f"Failed Puzzles:\n{json.dumps(report_data.get('failed_puzzles', []), indent=2)}\n\n"
            f"Game Results:\n{json.dumps(report_data.get('game_results', {}), indent=2)}\n\n"
            "Rewrite the code to fix these precise weaknesses while maintaining passing behaviors. "
            "Output the full updated chess AI server file."
        )

    # 3. API Invocation
    print(f"Calling Groq API to generate/improve {OUTPUT_FILE}...")
    client = Groq(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
    except Exception as e:
        print(f"Error during API call: {e}", file=sys.stderr)
        sys.exit(1)
        
    content = response.choices[0].message.content

    # 4. Output Extraction
    match = re.search(r"```python\s*(.*?)```", content, re.DOTALL)
    if not match:
        print("Error: Could not extract Python code from the LLM response.", file=sys.stderr)
        # print("Raw response:", content)
        sys.exit(1)
        
    python_code = match.group(1).strip()
    return python_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Builder Agent for Chess AI")
    parser.add_argument("--report", type=str, help="Path to the tester failure report JSON (optional)")
    args = parser.parse_args()

    # Generate the code
    code = generate_chess_agent(args.report)
    
    # 5. File Generation
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)
        
    print(f"Successfully generated and wrote {output_path}")
