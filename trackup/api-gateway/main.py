from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import os
import asyncio

app = FastAPI()

ROOM_SERVICE_URL = os.getenv("ROOM_SERVICE_URL", "http://localhost:8002")
GAME_ENGINE_URL = os.getenv("GAME_ENGINE_URL", "http://localhost:8003")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

# Proxy REST-запросы к room-service
def room_url(path: str) -> str:
    return f"{ROOM_SERVICE_URL}{path}"

def game_url(path: str) -> str:
    return f"{GAME_ENGINE_URL}{path}"

def user_url(path: str) -> str:
    return f"{USER_SERVICE_URL}{path}"

@app.api_route("/rooms{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def proxy_room(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=room_url(path),
            headers=request.headers.raw,
            content=await request.body()
        )
        return JSONResponse(status_code=resp.status_code, content=resp.json())

@app.api_route("/api/rooms{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def proxy_room_api(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=room_url(path),
            headers=request.headers.raw,
            content=await request.body()
        )
        return JSONResponse(status_code=resp.status_code, content=resp.json())

@app.api_route("/game{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def proxy_game(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=game_url(path),
            headers=request.headers.raw,
            content=await request.body()
        )
        return JSONResponse(status_code=resp.status_code, content=resp.json())

@app.api_route("/users{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def proxy_user(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=user_url(path),
            headers=request.headers.raw,
            content=await request.body()
        )
        return JSONResponse(status_code=resp.status_code, content=resp.json())

# WebSocket proxy для чата комнаты
@app.websocket("/ws/rooms/{room_id}/chat")
async def ws_proxy_room_chat(websocket: WebSocket, room_id: str):
    ws_url = f"{ROOM_SERVICE_URL.replace('http', 'ws')}/ws/rooms/{room_id}/chat"
    async with httpx.AsyncClient() as client:
        async with client.ws_connect(ws_url) as ws:
            await websocket.accept()
            async def to_client():
                async for msg in ws.iter_text():
                    await websocket.send_text(msg)
            async def to_service():
                while True:
                    data = await websocket.receive_text()
                    await ws.send_text(data)
            await asyncio.gather(to_client(), to_service())

# WebSocket proxy для игровых событий
@app.websocket("/ws/game/{room_id}")
async def ws_proxy_game_events(websocket: WebSocket, room_id: str):
    ws_url = f"{GAME_ENGINE_URL.replace('http', 'ws')}/ws/game/{room_id}"
    async with httpx.AsyncClient() as client:
        async with client.ws_connect(ws_url) as ws:
            await websocket.accept()
            async def to_client():
                async for msg in ws.iter_text():
                    await websocket.send_text(msg)
            async def to_service():
                while True:
                    data = await websocket.receive_text()
                    await ws.send_text(data)
            await asyncio.gather(to_client(), to_service())
