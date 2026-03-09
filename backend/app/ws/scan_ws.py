"""WebSocket endpoint for live scan output streaming."""

import json
import asyncio
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..config import settings

router = APIRouter()


@router.websocket("/ws/scans/{scan_id}")
async def scan_websocket(websocket: WebSocket, scan_id: int):
    """Stream live scan output to the frontend via WebSocket."""
    await websocket.accept()

    r = aioredis.from_url(settings.redis_url)
    pubsub = r.pubsub()
    channel = f"scan:{scan_id}"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=30.0)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)
                if data.get("output") == "__DONE__":
                    break
            else:
                # Send keepalive
                await websocket.send_json({"output": ""})
                await asyncio.sleep(0.1)
    except (WebSocketDisconnect, asyncio.TimeoutError, Exception):
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await r.close()
