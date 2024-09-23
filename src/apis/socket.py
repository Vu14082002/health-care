import asyncio
from typing import Dict, List
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        self.active_connections[conversation_id].remove(websocket)
        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def broadcast(self, conversation_id: str, message: str):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message)


class MessageSocket(WebSocketEndpoint):

    async def on_connect(self, websocket: WebSocket):  # type: ignore
        await websocket.accept()
        while True:
            await websocket.send_text("Message text was:")
            await asyncio.sleep(3)  # Sử dụng asyncio.sleep thay cho time.sleep

    async def on_receive(self, websocket: WebSocket, data):  # type: ignore
        await websocket.send_text(f"Message text was: {data}")

    async def on_disconnect(self, websocket: WebSocket, close_code):  # type: ignore
        pass
