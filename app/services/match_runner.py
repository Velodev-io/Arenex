import asyncio
import httpx
import chess
import logging
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import Match, Agent

logger = logging.getLogger(__name__)

# --- TTT Logic ---
def check_winner(board, mark):
    lines = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
    ]
    for line in lines:
        if all(board[r][c] == mark for r, c in line):
            return True
    return False

def ttt_is_full(board):
    return all(board[r][c] != "" for r in range(3) for c in range(3))

# --- ELO Calculation ---
def calculate_elo(elo_white: int, elo_black: int, result: str):
    """
    K=32, return generic integer points new for white and black.
    result in ('white_wins', 'black_wins', 'draw')
    """
    expected_w = 1 / (1 + 10 ** ((elo_black - elo_white) / 400))
    expected_b = 1 - expected_w

    if result == "white_wins":
        score_w, score_b = 1.0, 0.0
    elif result == "black_wins":
        score_w, score_b = 0.0, 1.0
    else:
        score_w, score_b = 0.5, 0.5

    new_white = int(elo_white + 32 * (score_w - expected_w))
    new_black = int(elo_black + 32 * (score_b - expected_b))
    return new_white, new_black

# --- Main Runner ---
async def process_match(match_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Match).where(Match.id == match_id))
        match = result.scalars().first()
        if not match:
            return

        res = await db.execute(select(Agent).where(Agent.id == match.agent_white_id))
        agent_white = res.scalars().first()
        res = await db.execute(select(Agent).where(Agent.id == match.agent_black_id))
        agent_black = res.scalars().first()

        if not agent_white or not agent_black:
            match.status = "finished"
            match.result = "invalid_agents"
            await db.commit()
            return
            
        game_type = agent_white.game_type
        
        # State Initialization
        if game_type == "chess":
            board = chess.Board()
        else:
            board = [["","",""],["","",""],["","",""]]

        history = []
        status = "live"
        match_result = None
        turn = "white"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                while status == "live":
                    current_agent = agent_white if turn == "white" else agent_black
                    endpoint = f"{str(current_agent.endpoint_url).rstrip('/')}/move"
                    
                    # Prepare Payload
                    if game_type == "chess":
                        payload = {
                            "board": board.fen(),
                            "your_color": turn,
                            "game_id": str(match_id),
                            "difficulty": 10
                        }
                    else:
                        payload = {
                            "board": board,
                            "your_mark": "X" if turn == "white" else "O",
                            "game_id": str(match_id)
                        }

                    logger.info(f"Match {match_id}: Requesting move from {turn} (ID: {current_agent.id})")
                    
                    try:
                        resp = await client.post(endpoint, json=payload)
                        resp.raise_for_status()
                        data = resp.json()
                    except Exception as e:
                        logger.error(f"Agent forfeit: {e}")
                        status = "finished"
                        match_result = "black_wins" if turn == "white" else "white_wins"
                        # Append forfeit notice
                        history.append({"agent": turn, "forfeit": True, "reason": str(e)})
                        break

                    # Validate Move
                    try:
                        if game_type == "chess":
                            move_uci = data.get("move")
                            if not move_uci:
                                raise ValueError("Missing 'move' in response")
                            move = chess.Move.from_uci(move_uci)
                            if move not in board.legal_moves:
                                raise ValueError("Illegal move")
                            board.push(move)
                            history.append({"agent": turn, "move": move_uci, "fen": board.fen(), "reasoning": data.get("reasoning", "")})

                            if board.is_checkmate():
                                status = "finished"
                                match_result = "white_wins" if turn == "white" else "black_wins"
                            elif board.is_game_over():
                                status = "finished"
                                match_result = "draw"

                        else:
                            # TTT logic
                            r, c = data.get("row"), data.get("col")
                            if r is None or c is None or board[r][c] != "":
                                raise ValueError("Illegal cell selection")
                            mark = "X" if turn == "white" else "O"
                            board[r][c] = mark
                            
                            # Log History
                            history.append({
                                "agent": turn,
                                "move": {"row": r, "col": c},
                                "board": [row[:] for row in board],
                                "reasoning": data.get("reasoning", "")
                            })
                            
                            if check_winner(board, mark):
                                status = "finished"
                                match_result = "white_wins" if turn == "white" else "black_wins"
                            elif ttt_is_full(board):
                                status = "finished"
                                match_result = "draw"

                    except Exception as e:
                        logger.error(f"Agent forfeit on bad move: {e}")
                        status = "finished"
                        match_result = "black_wins" if turn == "white" else "white_wins"
                        history.append({"agent": turn, "forfeit": True, "reason": f"Bad move: {e}"})
                        break

                    # Flop turn
                    turn = "black" if turn == "white" else "white"

                    # Database pumping
                    match.history = list(history)  # Shallow copy ensures JSON compatibility tracking
                    await db.commit()

        except Exception as e:
            logger.error(f"Match loop crashed: {e}")
            status = "finished"
            match_result = "draw"

        # Resolve match
        logger.info(f"Match {match_id} completed. Result: {match_result}")
        match.status = "finished"
        match.result = match_result
        match.history = history
        
        if match_result:
            new_w, new_b = calculate_elo(agent_white.elo, agent_black.elo, match_result)
            agent_white.elo = new_w
            agent_black.elo = new_b
            match.history.append({"event": "elo_updated", "white": new_w, "black": new_b})
            
        await db.commit()

async def run_match(match_id: int):
    # Wrapper to launch the task synchronously inside FastAPI BackgroundTasks
    asyncio.create_task(process_match(match_id))
