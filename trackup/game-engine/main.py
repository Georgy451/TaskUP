from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import redis.asyncio as aioredis
import uuid
import os
from enum import Enum
from datetime import datetime
import asyncio

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class GameState(str, Enum):
    waiting = "waiting"
    started = "started"
    voting = "voting"
    finished = "finished"

class GameEvent(BaseModel):
    type: str  # start, turn, vote, end, custom
    payload: dict
    timestamp: float = None

class GameSession(BaseModel):
    session_id: str
    room_id: str
    state: GameState = GameState.waiting
    players: list[str]
    current_player: str = None
    events: list[GameEvent] = []
    started_at: float = None
    finished_at: float = None

@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

@app.post("/game/start")
async def start_game(room_id: str, players: list[str]):
    redis = app.state.redis
    session_id = str(uuid.uuid4())
    session = GameSession(
        session_id=session_id,
        room_id=room_id,
        state=GameState.started,
        players=players,
        current_player=players[0],
        started_at=datetime.utcnow().timestamp(),
        events=[]
    )
    await redis.set(f"game:{room_id}", session.json())
    await redis.publish(f"game:{room_id}:pubsub", GameEvent(type="start", payload={"session_id": session_id, "players": players}, timestamp=datetime.utcnow().timestamp()).json())
    return session

@app.post("/game/{room_id}/event")
async def game_event(room_id: str, event: GameEvent):
    redis = app.state.redis
    session_raw = await redis.get(f"game:{room_id}")
    if not session_raw:
        raise HTTPException(status_code=404, detail="Game session not found")
    session = GameSession.parse_raw(session_raw)
    session.events.append(event)
    # Пример: смена состояния и текущего игрока
    if event.type == "turn":
        idx = session.players.index(session.current_player)
        session.current_player = session.players[(idx + 1) % len(session.players)]
    if event.type == "vote":
        session.state = GameState.voting
    if event.type == "end":
        session.state = GameState.finished
        session.finished_at = datetime.utcnow().timestamp()
    await redis.set(f"game:{room_id}", session.json())
    await redis.publish(f"game:{room_id}:pubsub", event.json())
    return session

@app.get("/game/{room_id}", response_model=GameSession)
async def get_game_session(room_id: str):
    redis = app.state.redis
    session_raw = await redis.get(f"game:{room_id}")
    if not session_raw:
        raise HTTPException(status_code=404, detail="Game session not found")
    return GameSession.parse_raw(session_raw)

@app.websocket("/ws/game/{room_id}")
async def websocket_game_events(websocket: WebSocket, room_id: str):
    await websocket.accept()
    redis = app.state.redis
    pubsub = redis.pubsub()
    channel = f"game:{room_id}:pubsub"
    await pubsub.subscribe(channel)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg["type"] == "message":
                await websocket.send_text(msg["data"])
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Клиент может отправлять события через WebSocket (опционально)
                await redis.publish(channel, data)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
