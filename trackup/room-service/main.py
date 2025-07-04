from fastapi import FastAPI, HTTPException, Body, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import redis.asyncio as aioredis
import uuid
import os
from typing import Optional
from enum import Enum
from datetime import datetime
import asyncio
import httpx
import json

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")


class RoomState(str, Enum):
    waiting = "waiting"
    started = "started"
    finished = "finished"

class Room(BaseModel):
    id: str
    name: str
    creator: str
    participants: list[str] = []
    state: RoomState = RoomState.waiting


class RoomCreate(BaseModel):
    name: str
    creator: str

class JoinRoomRequest(BaseModel):
    nickname: str

class RoomStateUpdate(BaseModel):
    state: RoomState
    user: str

class ChatMessage(BaseModel):
    user: str
    message: str
    timestamp: float = None

class GameEvent(BaseModel):
    type: str 
    payload: dict
    timestamp: float = None

class GameSession(BaseModel):
    room_id: str
    session_id: str
    started_at: float
    finished_at: float
    participants: list[str]
    events: list[GameEvent]
    winner: str = None

@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

@app.post("/rooms", response_model=Room)
async def create_room(room: RoomCreate):
    redis = app.state.redis
    room_id = str(uuid.uuid4())
    room_data = Room(id=room_id, name=room.name, creator=room.creator)
    import json
    data = room_data.dict()
    for k, v in data.items():
        if v is None:
            data[k] = ""
        elif isinstance(v, (list, dict)):
            data[k] = json.dumps(v)
        else:
            data[k] = str(v)
    print("DEBUG: data for redis.hset:", data)
    await redis.hset(f"room:{room_id}", mapping=data)
    await redis.expire(f"room:{room_id}", 1800)  # TTL 30 мин
    return room_data

@app.delete("/rooms/{room_id}")
async def delete_room(room_id: str):
    redis = app.state.redis
    deleted = await redis.delete(f"room:{room_id}")
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"detail": "Room deleted"}

@app.post("/rooms/{room_id}/join")
async def join_room(room_id: str, req: JoinRoomRequest):
    redis = app.state.redis
    key = f"room:{room_id}"
    room = await redis.hgetall(key)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    participants = eval(room.get("participants", "[]"))
    if req.nickname in participants:
        raise HTTPException(status_code=400, detail="Nickname already taken")
    participants.append(req.nickname)
    await redis.hset(key, "participants", str(participants))
    return {"detail": f"{req.nickname} joined room {room_id}"}

@app.post("/rooms/{room_id}/state")
async def update_room_state(room_id: str, req: RoomStateUpdate):
    redis = app.state.redis
    key = f"room:{room_id}"
    room = await redis.hgetall(key)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if req.user != room.get("creator"):
        raise HTTPException(status_code=403, detail="Only creator can change state")
    await redis.hset(key, "state", req.state)
    return {"detail": f"Room state updated to {req.state}"}

@app.get("/rooms/{room_id}/state")
async def get_room_state(room_id: str):
    redis = app.state.redis
    key = f"room:{room_id}"
    state = await redis.hget(key, "state")
    if not state:
        raise HTTPException(status_code=404, detail="Room not found or state not set")
    return {"state": state}

@app.get("/rooms/{room_id}", response_model=Room)
async def get_room(room_id: str):
    redis = app.state.redis
    key = f"room:{room_id}"
    room = await redis.hgetall(key)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room["participants"] = eval(room.get("participants", "[]"))
    return Room(**room)

@app.post("/rooms/{room_id}/chat/send")
async def send_chat_message(room_id: str, msg: ChatMessage):
    redis = app.state.redis
    key = f"room:{room_id}:chat"
    msg.timestamp = msg.timestamp or datetime.utcnow().timestamp()
    await redis.rpush(key, msg.json())
    await redis.publish(f"room:{room_id}:chat:pubsub", msg.json())
    # Храним только последние 100 сообщений
    await redis.ltrim(key, -100, -1)
    return {"detail": "Message sent"}

@app.get("/rooms/{room_id}/chat/messages")
async def get_chat_messages(room_id: str, limit: int = 30):
    redis = app.state.redis
    key = f"room:{room_id}:chat"
    messages = await redis.lrange(key, -limit, -1)
    return [ChatMessage.parse_raw(m) for m in messages]

@app.websocket("/ws/rooms/{room_id}/chat")
async def websocket_room_chat(websocket: WebSocket, room_id: str):
    await websocket.accept()
    redis = app.state.redis
    pubsub = redis.pubsub()
    channel = f"room:{room_id}:chat:pubsub"
    await pubsub.subscribe(channel)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg["type"] == "message":
                await websocket.send_text(msg["data"])
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Клиент может отправлять сообщения через WebSocket (опционально)
                await redis.rpush(f"room:{room_id}:chat", data)
                await redis.publish(channel, data)
                await redis.ltrim(f"room:{room_id}:chat", -100, -1)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

@app.post("/rooms/{room_id}/game/event")
async def send_game_event(room_id: str, event: GameEvent):
    redis = app.state.redis
    key = f"room:{room_id}:events"
    event.timestamp = event.timestamp or datetime.utcnow().timestamp()
    await redis.rpush(key, event.json())
    await redis.publish(f"room:{room_id}:game:pubsub", event.json())
    await redis.ltrim(key, -100, -1)
    return {"detail": "Event sent"}

@app.get("/rooms/{room_id}/game/events")
async def get_game_events(room_id: str, limit: int = 30):
    redis = app.state.redis
    key = f"room:{room_id}:events"
    events = await redis.lrange(key, -limit, -1)
    return [GameEvent.parse_raw(e) for e in events]

@app.websocket("/ws/rooms/{room_id}/game")
async def websocket_room_game(websocket: WebSocket, room_id: str):
    await websocket.accept()
    redis = app.state.redis
    pubsub = redis.pubsub()
    channel = f"room:{room_id}:game:pubsub"
    await pubsub.subscribe(channel)
    try:
        while True:
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg and msg["type"] == "message":
                await websocket.send_text(msg["data"])
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                # Клиент может отправлять события через WebSocket (опционально)
                await redis.rpush(f"room:{room_id}:events", data)
                await redis.publish(channel, data)
                await redis.ltrim(f"room:{room_id}:events", -100, -1)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

async def notify_user_service(session: GameSession):
    async with httpx.AsyncClient() as client:
        for user in session.participants:
            await client.post(f"{USER_SERVICE_URL}/users/{user}/stats/update", json={
                "room_id": session.room_id,
                "session_id": session.session_id,
                "winner": session.winner,
                "events": [e.dict() for e in session.events],
                "finished_at": session.finished_at
            })

@app.post("/rooms/{room_id}/game/finish")
async def finish_game_session(room_id: str, winner: str = None):
    redis = app.state.redis
    key = f"room:{room_id}"
    events_key = f"room:{room_id}:events"
    room = await redis.hgetall(key)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    events = await redis.lrange(events_key, 0, -1)
    session_id = str(uuid.uuid4())
    session = GameSession(
        room_id=room_id,
        session_id=session_id,
        started_at=float(room.get("created_at", datetime.utcnow().timestamp())),
        finished_at=datetime.utcnow().timestamp(),
        participants=eval(room.get("participants", "[]")),
        events=[GameEvent.parse_raw(e) for e in events],
        winner=winner
    )
    await redis.rpush(f"history:{room_id}", session.json())
    await redis.delete(events_key)
    await notify_user_service(session)
    return {"detail": "Game session saved", "session_id": session_id}

@app.get("/rooms/{room_id}/history")
async def get_room_history(room_id: str, limit: int = 10):
    redis = app.state.redis
    key = f"history:{room_id}"
    sessions = await redis.lrange(key, -limit, -1)
    return [GameSession.parse_raw(s) for s in sessions]

@app.get("/rooms/{room_id}/history/{session_id}")
async def get_session_detail(room_id: str, session_id: str):
    redis = app.state.redis
    key = f"history:{room_id}"
    sessions = await redis.lrange(key, 0, -1)
    for s in sessions:
        session = GameSession.parse_raw(s)
        if session.session_id == session_id:
            return session
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/users/{user_id}/stats")
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="User stats not found")
        return resp.json()
