from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as aioredis
import uuid
import os
from enum import Enum
from datetime import datetime
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретный адрес фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    participants: list[str]
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
    exists = await redis.exists(f"room:{room.name}")
    if exists:
        raise HTTPException(status_code=400, detail="Код комнаты уже занят")
    # Сохраняем участников как json-строку только для Redis
    await redis.hset(f"room:{room.name}", mapping={
        "id": room.name,
        "name": room.name,
        "creator": room.participants[0],
        "mode": room.mode,
        "participants": json.dumps(room.participants, ensure_ascii=False),
        "state": RoomState.waiting.value
    })
    await redis.expire(f"room:{room.name}", 1800)
    session = {
        "room_id": room.name,
        "name": room.name,
        "mode": room.mode,
        "participants": json.dumps(room.participants, ensure_ascii=False),
        "state": RoomState.waiting.value,
        "created_at": datetime.utcnow().timestamp()
    }
    await redis.hset(f"game_session:{room.name}", mapping=session)
    await redis.expire(f"game_session:{room.name}", 1800)
    print("Возвращаем room_data:", room.dict())
    # Возвращаем объект Room с participants как список
    return Room(
        id=room.name,
        name=room.name,
        creator=room.participants[0],
        mode=room.mode,
        participants=room.participants,
        state=RoomState.waiting
    )
