"""WebSocket endpoint for live AutoPentest toolchain output streaming."""

from __future__ import annotations

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import settings

router = APIRouter()


@router.websocket("/ws/toolchains/{run_id}")
async def toolchain_websocket(websocket: WebSocket, run_id: int):
    await websocket.accept()

    r = aioredis.from_url(settings.redis_url)
    pubsub = r.pubsub()
    channel = f"toolchain:{run_id}"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await asyncio.wait_for(pubsub.get_message(ignore_subscribe_messages=True), timeout=30.0)
            if message and message.get("type") == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)
                if data.get("output") == "__DONE__":
                    break
            else:
                await websocket.send_json({"output": ""})
                await asyncio.sleep(0.1)
    except (WebSocketDisconnect, asyncio.TimeoutError, Exception):
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await r.close()
