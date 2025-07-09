from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List
import redis.asyncio as aioredis
import os

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Модель для подключения к комнате
class JoinRequest(BaseModel):
    room_id: str
    username: str

@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()

@app.post("/join")
async def join_room(req: JoinRequest):
    redis = app.state.redis
    key = f"room:{req.room_id}:participants"
    # Добавляем пользователя в список участников комнаты
    await redis.sadd(key, req.username)
    return {"message": f"Пользователь {req.username} присоединился к комнате {req.room_id}"}

@app.get("/participants", response_model=List[str])
async def get_participants(room_id: str = Query(...)):
    redis = app.state.redis
    key = f"room:{room_id}:participants"
    participants = await redis.smembers(key)
    return sorted(participants)

# ...сюда будет добавлена новая логика игрового движка...
