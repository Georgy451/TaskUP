from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as aioredis
import uuid
import os
from enum import Enum
from datetime import datetime

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RoomState(str, Enum):
    waiting = "waiting"
    started = "started"
    finished = "finished"

class Room(BaseModel):
    id: str
    name: str
    creator: str
    mode: str
    participants: list[str] = []
    state: RoomState = RoomState.waiting

class RoomCreate(BaseModel):
    name: str
    creator: str
    mode: str

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
    room_data = Room(id=room_id, name=room.name, creator=room.creator, mode=room.mode)
    await redis.hset(f"room:{room_id}", mapping=room_data.dict())
    await redis.expire(f"room:{room_id}", 1800)  # TTL 30 мин
    # Создаём игровую сессию сразу при создании комнаты
    session = {
        "room_id": room_id,
        "name": room.name,
        "mode": room.mode,
        "participants": str(room_data.participants),
        "state": room_data.state.value,
        "created_at": datetime.utcnow().timestamp()
    }
    await redis.hset(f"game_session:{room_id}", mapping=session)
    await redis.expire(f"game_session:{room_id}", 1800)
    return room_data
