"""
chess_tester.py
---------------
Standalone test suite evaluating the `chess_ai_server.py`.
Runs tactical puzzles, random-opponent games, and stability mirror games.
Produces a structured JSON report.

Implemented from spec: agents/chess/tester_agent.md
"""

import argparse
import json
import random
import time
from typing import Optional, Tuple

import chess
import requests

# Constants
DEFAULT_URL = "http://localhost:8001"
REQUEST_TIMEOUT = 5       # Seconds to wait for /move
PASS_RATE_THRESHOLD = 0.8 # Minimum score to be considered passing

# ---------------------------------------------------------------------------
# Suite 1: Tactical Puzzles — outcome-validated, not move-string-matched
# ---------------------------------------------------------------------------
# Each puzzle defines a "validator" key: a callable(board_before, move_uci) -> (passed: bool, reason: str)
# Using python-chess to check the *result* of the move, not its exact UCI string.

def _validate_mate_in_one(board_before: chess.Board, move_uci: str):
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        b = board_before.copy()
        b.push(move)
        if b.is_checkmate():
            return True, "Correctly delivers checkmate"
        return False, f"Move {move_uci} does not result in checkmate"
    except Exception as e:
        return False, str(e)

def _validate_captures_highest(board_before: chess.Board, move_uci: str):
    """Pass if the move captures a piece AND the resulting material gain is the maximum achievable."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        # Find all captures and their material value
        PIECE_VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        best_gain = 0
        for m in board_before.legal_moves:
            if board_before.is_capture(m):
                victim = board_before.piece_at(m.to_square)
                if victim:
                    best_gain = max(best_gain, PIECE_VALUE.get(victim.piece_type, 0))
        if best_gain == 0:
            return False, "No captures available in position"
        if not board_before.is_capture(move):
            return False, f"Move {move_uci} is not a capture (best available gain: +{best_gain})"
        victim = board_before.piece_at(move.to_square)
        gain = PIECE_VALUE.get(victim.piece_type, 0) if victim else 0
        if gain == best_gain:
            return True, f"Correctly captures highest-value piece (+{gain})"
        return False, f"Move {move_uci} gains +{gain} but best available is +{best_gain}"
    except Exception as e:
        return False, str(e)

def _validate_saves_piece(board_before: chess.Board, move_uci: str):
    """Pass if the most valuable attacked own piece is no longer attacked or captured by the move."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        PIECE_VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        # Find pieces under attack before the move
        turn = board_before.turn
        attacked = []
        for sq in chess.SQUARES:
            p = board_before.piece_at(sq)
            if p and p.color == turn and board_before.is_attacked_by(not turn, sq):
                attacked.append((PIECE_VALUE.get(p.piece_type, 0), sq, p))
        if not attacked:
            return False, "No pieces are under attack in this position"
        attacked.sort(reverse=True)
        most_valuable_val, most_valuable_sq, most_valuable_piece = attacked[0]
        b = board_before.copy()
        b.push(move)
        # Check if that piece is still there and still attacked
        if b.piece_at(most_valuable_sq) is None:
            # Piece moved away or was captured in the process — check if it was moved
            return True, f"Correctly moved {most_valuable_piece} out of danger"
        still_attacked = b.is_attacked_by(turn, most_valuable_sq)  # now it's opponent's turn
        if not still_attacked:
            return True, f"Correctly defended the {most_valuable_piece} at {chess.square_name(most_valuable_sq)}"
        return False, f"The {most_valuable_piece} at {chess.square_name(most_valuable_sq)} is still under attack after {move_uci}"
    except Exception as e:
        return False, str(e)

def _validate_castles(board_before: chess.Board, move_uci: str):
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        if board_before.is_castling(move):
            return True, f"Correctly castles with {move_uci}"
        # If castling is available, not castling is wrong
        can_castle = (
            board_before.has_kingside_castling_rights(board_before.turn) or
            board_before.has_queenside_castling_rights(board_before.turn)
        )
        if can_castle:
            return False, f"Castling was available but {move_uci} was played instead"
        return True, "No castling rights — any legal move is fine"
    except Exception as e:
        return False, str(e)

def _validate_avoids_check(board_before: chess.Board, move_uci: str):
    """Pass if king is not in check after the move."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        # All legal moves already avoid self-check — any legal move passes
        return True, f"Move {move_uci} is legal (avoids self-check by definition)"
    except Exception as e:
        return False, str(e)

def _validate_delivers_check(board_before: chess.Board, move_uci: str):
    """Pass if the move results in check or checkmate."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        b = board_before.copy()
        b.push(move)
        if b.is_check() or b.is_checkmate():
            return True, f"Correctly delivers check/checkmate with {move_uci}"
        return False, f"Move {move_uci} does not deliver check"
    except Exception as e:
        return False, str(e)

def _validate_develops_piece(board_before: chess.Board, move_uci: str):
    """Pass if a minor piece (knight or bishop) moves forward."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move not in board_before.legal_moves:
            return False, f"Illegal move {move_uci}"
        piece = board_before.piece_at(move.from_square)
        if piece and piece.piece_type in (chess.KNIGHT, chess.BISHOP):
            return True, f"Correctly develops {chess.piece_name(piece.piece_type)} with {move_uci}"
        # A central pawn push is also valid development
        if piece and piece.piece_type == chess.PAWN:
            center = {chess.E4, chess.D4, chess.E5, chess.D5}
            if move.to_square in center:
                return True, f"Correctly pushes central pawn to {chess.square_name(move.to_square)}"
        return False, f"Move {move_uci} does not develop a piece"
    except Exception as e:
        return False, str(e)

def _validate_any_legal(board_before: chess.Board, move_uci: str):
    """Pass if the move is legal — used for positions where any legal move is fine."""
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board_before.legal_moves:
            return True, f"Legal move {move_uci} played"
        return False, f"Illegal move {move_uci}"
    except Exception as e:
        return False, str(e)


TACTICAL_PUZZLES = [
    {
        "scenario": "mate_in_one",
        "description": "Mate in one — back rank checkmate",
        "fen": "6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1",
        "color": "white",
        "validator": _validate_mate_in_one,
    },
    {
        "scenario": "free_queen",
        "description": "Capture free queen",
        "fen": "3q2k1/8/8/8/8/8/8/3R2K1 w - - 0 1",
        "color": "white",
        "validator": _validate_captures_highest,
    },
    {
        "scenario": "hanging_queen",
        "description": "Save own hanging queen",
        "fen": "3Q2k1/8/8/8/8/8/8/3r2K1 w - - 0 1",
        "color": "white",
        "validator": _validate_saves_piece,
    },
    {
        "scenario": "capture_highest_value",
        "description": "Capture highest value piece safely (Queen vs Pawn)",
        "fen": "3q2k1/3p4/8/8/8/8/8/3R2K1 w - - 0 1",
        "color": "white",
        "validator": _validate_captures_highest,
    },
    {
        "scenario": "castle",
        "description": "Castle kingside effectively",
        "fen": "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1",
        "color": "white",
        "validator": _validate_castles,
    },
    {
        "scenario": "center_control",
        "description": "Control center square opening",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "color": "white",
        "validator": _validate_develops_piece,
    },
    {
        "scenario": "avoid_self_check",
        "description": "Avoid moving into check",
        "fen": "4k3/4r3/8/8/8/8/8/4K3 w - - 0 1",
        "color": "white",
        "validator": _validate_avoids_check,
    },
    {
        "scenario": "check_fork",
        "description": "Deliver check to gain tempo",
        "fen": "4k3/8/8/8/8/8/8/R3K3 w Q - 0 1",
        "color": "white",
        "validator": _validate_delivers_check,
    },
    {
        "scenario": "development",
        "description": "Develop pieces effectively",
        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "color": "black",
        "validator": _validate_develops_piece,
    },
    {
        "scenario": "avoid_illegal_move",
        "description": "Avoid illegal moves (pinned piece)",
        "fen": "4k3/8/8/8/4r3/8/4P3/4K3 w - - 0 1",
        "color": "white",
        "validator": _validate_avoids_check,
    },
]

# ---------------------------------------------------------------------------
# Runner Functions
# ---------------------------------------------------------------------------

def wait_for_server(url: str, retries: int = 15, delay: float = 1.0) -> bool:
    """Poll the /health endpoint until available."""
    print(f"Waiting for agent server at {url}...")
    for _ in range(retries):
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.status_code == 200:
                print("Server is ready.")
                return True
        except requests.RequestException:
            pass
        time.sleep(delay)
    return False

def request_move(url: str, fen: str, color: str, game_id: str) -> dict:
    """Helper to request a move from the agent server."""
    payload = {
        "board": fen,
        "your_color": color,
        "game_id": game_id
    }
    resp = requests.post(f"{url}/move", json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

def run_suite_1_tactics(agent_url: str) -> Tuple[list, list]:
    passed = []
    failed = []

    for idx, puzzle in enumerate(TACTICAL_PUZZLES):
        try:
            data = request_move(agent_url, puzzle["fen"], puzzle["color"], f"puzzle_{idx}")
            agent_move = data.get("move", "")
            reasoning = data.get("reasoning", "No reasoning provided")

            board_before = chess.Board(puzzle["fen"])
            ok, reason = puzzle["validator"](board_before, agent_move)

            if ok:
                passed.append(puzzle)
            else:
                failed.append({
                    "scenario": puzzle["scenario"],
                    "description": puzzle["description"],
                    "board_fen": puzzle["fen"],
                    "validation_failure": reason,
                    "agent_move": agent_move,
                    "reasoning_given": reasoning,
                })
        except Exception as e:
            failed.append({
                "scenario": puzzle["scenario"],
                "description": puzzle["description"],
                "board_fen": puzzle["fen"],
                "validation_failure": "Exception during test",
                "agent_move": "ERROR",
                "reasoning_given": str(e),
            })

    return passed, failed

def run_suite_2_vs_random(agent_url: str, games: int = 5) -> dict:
    results = {"wins": 0, "losses": 0, "draws": 0, "crashes": 0, "timeouts": 0}

    for i in range(games):
        play_as = "white" if i % 2 == 0 else "black"
        board = chess.Board()

        while not board.is_game_over() and len(board.move_stack) < 200:
            current_turn = "white" if board.turn == chess.WHITE else "black"

            if current_turn == play_as:
                # Agent turn
                try:
                    data = request_move(agent_url, board.fen(), play_as, f"random_{i}")
                    move = chess.Move.from_uci(data["move"])
                    if move in board.legal_moves:
                        board.push(move)
                    else:
                        results["crashes"] += 1
                        break
                except requests.Timeout:
                    results["timeouts"] += 1
                    break
                except Exception:
                    results["crashes"] += 1
                    break
            else:
                # Random opponent turn
                moves = list(board.legal_moves)
                board.push(random.choice(moves))

        # Tally result
        if board.is_game_over():
            winner = board.outcome().winner
            if winner is None:
                results["draws"] += 1
            elif (winner == chess.WHITE and play_as == "white") or (winner == chess.BLACK and play_as == "black"):
                results["wins"] += 1
            else:
                results["losses"] += 1

    return results

def run_suite_3_mirror(agent_url: str, games: int = 3) -> dict:
    results = {"crashes": 0, "timeouts": 0, "loops": 0}

    for i in range(games):
        board = chess.Board()
        seen_positions = {}

        while not board.is_game_over() and len(board.move_stack) < 200:
            current_color = "white" if board.turn == chess.WHITE else "black"

            # Loop detection (simple repetition check based on FEN)
            fen_base = board.fen().split(" ")[0]
            seen_positions[fen_base] = seen_positions.get(fen_base, 0) + 1
            if seen_positions[fen_base] >= 3:
                results["loops"] += 1
                break

            try:
                data = request_move(agent_url, board.fen(), current_color, f"mirror_{i}")
                move = chess.Move.from_uci(data["move"])

                if move in board.legal_moves:
                    board.push(move)
                else:
                    results["crashes"] += 1
                    break
            except requests.Timeout:
                results["timeouts"] += 1
                break
            except Exception:
                results["crashes"] += 1
                break

    return results

def interpret_weaknesses(failed_puzzles: list, random_res: dict, mirror_res: dict) -> list:
    weaknesses = []

    # Analyze puzzles
    puzzle_counts = {}
    for failure in failed_puzzles:
        s = failure["scenario"]
        puzzle_counts[s] = puzzle_counts.get(s, 0) + 1

    for scenario, count in puzzle_counts.items():
        weaknesses.append(f"Agent failed {count} '{scenario}' puzzle(s).")

    # Analyze random games
    if random_res["losses"] > 0:
        weaknesses.append(f"Agent lost {random_res['losses']}/{random_res['wins'] + random_res['losses'] + random_res['draws']} games vs random opponent (should win 100%).")
    if random_res["crashes"] > 0 or random_res["timeouts"] > 0:
        weaknesses.append(f"Agent experienced {random_res['crashes']} crashes and {random_res['timeouts']} timeouts playing vs random.")

    # Analyze mirror games
    if mirror_res["crashes"] > 0 or mirror_res["timeouts"] > 0 or mirror_res["loops"] > 0:
        weaknesses.append(f"Agent mirror games displayed instability: {mirror_res['crashes']} crashes, {mirror_res['timeouts']} timeouts, {mirror_res['loops']} infinite loops.")

    return weaknesses

def run(agent_url: str = DEFAULT_URL, output_path: str = "tester_report.json"):
    print("\n--- Starting Tester Agent ---")
    if not wait_for_server(agent_url):
        print("Server not responding. Tester aborting.")
        return {"passed": False, "pass_rate": 0.0}

    print("Running Suite 1: Tactical Puzzles...")
    passed_puzzles, failed_puzzles = run_suite_1_tactics(agent_url)

    print("Running Suite 2: Games vs Random...")
    random_results = run_suite_2_vs_random(agent_url, games=5)

    print("Running Suite 3: Mirror Games...")
    mirror_results = run_suite_3_mirror(agent_url, games=3)

    # Calculate consolidated stats
    total_puzzles = len(TACTICAL_PUZZLES)
    total_games = 5 + 3 # 5 random, 3 mirror
    total_metrics = total_puzzles + total_games

    # Calculate failures across all suites to define pass_rate
    # Loss against random or any crash/loop counts as a metric failure
    puzzle_fails = len(failed_puzzles)
    game_fails = random_results["losses"] + random_results["crashes"] + random_results["timeouts"] \
                 + mirror_results["crashes"] + mirror_results["timeouts"] + mirror_results["loops"]

    total_failures = puzzle_fails + game_fails
    pass_rate = max(0.0, (total_metrics - total_failures) / total_metrics)

    weaknesses = interpret_weaknesses(failed_puzzles, random_results, mirror_results)

    report = {
        "pass_rate": pass_rate,
        "threshold": PASS_RATE_THRESHOLD,
        "passed": pass_rate >= PASS_RATE_THRESHOLD,
        "failed_puzzles": failed_puzzles,
        "game_results": {
            "vs_random": random_results,
            "vs_mirror": mirror_results
        },
        "identified_weaknesses": weaknesses
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Testing complete. Pass rate: {pass_rate*100:.1f}%")
    print(f"Report saved to {output_path}")

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tester Agent for Chess AI")
    parser.add_argument("--url", type=str, default=DEFAULT_URL, help="Agent server URL")
    parser.add_argument("--output", type=str, default="tester_report.json", help="Output JSON path")
    args = parser.parse_args()

    run(agent_url=args.url, output_path=args.output)
