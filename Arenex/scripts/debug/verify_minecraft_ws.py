import asyncio
import websockets
import json
import os

async def test_ws():
    match_id = os.getenv("MATCH_ID", "1")
    uri = f"ws://localhost:8000/ws/matches/{match_id}/minecraft"
    headers = {"Origin": "http://localhost:5173"}
    try:
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            print("Connected to Minecraft WebSocket")
            # This will wait for a message or timeout
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    payload = json.loads(message)
                    if payload.get("type") in {"match_start", "state_update"}:
                        print(f"viewer_url={payload.get('viewer_url')}")
                    print(f"Received: {payload}")
                except asyncio.TimeoutError:
                    print("Timeout waiting for message (expected if no match is running)")
                    break
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
