from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis.asyncio as aioredis
import uuid
import os
from enum import Enum
from datetime import datetime
import json

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
    id: str  # теперь пользователь вводит id (код комнаты)
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
    # Проверяем, что такой код комнаты ещё не занят
    exists = await redis.exists(f"room:{room.id}")
    if exists:
        raise HTTPException(status_code=400, detail="Код комнаты уже занят")
    # Преобразуем список участников в строку для Redis
    room_dict = Room(id=room.id, name=room.name, creator=room.creator, mode=room.mode).dict()
    room_dict["participants"] = json.dumps(room_dict["participants"], ensure_ascii=False)
    await redis.hset(f"room:{room.id}", mapping=room_dict)
    await redis.expire(f"room:{room.id}", 1800)  # TTL 30 мин
    # Создаём игровую сессию сразу при создании комнаты
    session = {
        "room_id": room.id,
        "name": room.name,
        "mode": room.mode,
        "participants": room_dict["participants"],
        "state": room_dict["state"],
        "created_at": datetime.utcnow().timestamp()
    }
    await redis.hset(f"game_session:{room.id}", mapping=session)
    await redis.expire(f"game_session:{room.id}", 1800)
    print("Возвращаем room_data:", json.dumps(room_dict, ensure_ascii=False))
    try:
        return Room(**{**room_dict, "participants": []})
    except Exception as e:
        print("Ошибка при возврате room_data:", e)
        raise HTTPException(status_code=500, detail=f"Ошибка сериализации: {e}")
