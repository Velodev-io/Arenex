import asyncio
import websockets
import json
import requests
import os
import subprocess
import time

async def test_websocket(match_id):
    uri = f"ws://localhost:8089/ws/matches/{match_id}"
    logger.info(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            # 1. Expect catchup
            msg = await websocket.recv()
            data = json.loads(msg)
            logger.info(f"Received initial event: {data['type']} (Status: {data.get('status')}, History size: {len(data.get('history', []))})")
            
            # 2. Listen for moves
            logger.info("Listening for moves...")
            # Use asyncio.wait_for instead of timeout param
            while True:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=15)
                    data = json.loads(msg)
                    logger.info(f"Received event: {data['type']}")
                    if data['type'] == 'finished':
                        logger.info("Match finished event received.")
                        break
                    if data['type'] == 'move':
                        logger.info(f"Move received: {data['data'].get('move')}")
                        # We saw a move, mission accomplished
                        break
                except asyncio.TimeoutError:
                    logger.info("Timeout waiting for move.")
                    break
    except Exception as e:
        logger.info(f"WebSocket test failed: {e}")

def run_all():
    # Start fresh platform
    platform_proc = subprocess.Popen(
        ["venv/bin/uvicorn", "app.main:app", "--port", "8089", "--host", "0.0.0.0"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(5)
    agent_proc = subprocess.Popen(
        ["venv/bin/uvicorn", "Tic-Tac-ToeAgent.agent:app", "--port", "8012", "--host", "0.0.0.0"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(3)

    try:
        r1 = requests.post("http://localhost:8089/agents/", json={"name": "WSBotA", "endpoint_url": "http://localhost:8012", "game_type": "tictactoe"})
        r2 = requests.post("http://localhost:8089/agents/", json={"name": "WSBotB", "endpoint_url": "http://localhost:8012", "game_type": "tictactoe"})
        a1, a2 = r1.json()['id'], r2.json()['id']
        rm = requests.post("http://localhost:8089/matches/", json={"agent_white_id": a1, "agent_black_id": a2})
        match_id = rm.json()['id']
        time.sleep(1)
        asyncio.run(test_websocket(match_id))
    finally:
        platform_proc.terminate()
        agent_proc.terminate()

if __name__ == "__main__":
    run_all()
