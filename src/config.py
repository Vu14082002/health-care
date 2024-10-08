from typing import Any, Dict, List, Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings
from starlette.websockets import WebSocket


class Config(BaseSettings):
    class Config:
        env_file = ".env"

    ENV: str = "STAG"
    SENTRY_DSN: Optional[str] = None
    REDIS_URL: str
    REDIS_URL_WORKING_TIME: str
    BROKER_URL: str = Field(alias="broker_url")
    CELERY_ROUTES: dict = Field(
        default={
            "worker.on_admin_action": {"queue": "admin_queue"},
        },
        alias="task_routes",
    )
    CELERY_IMPORTS: list = Field(default=["src.tasks"], alias="imports")
    CELERY_RESULT_BACKEND: str = Field(default="rpc://", alias="result_backend")
    CELERY_TRACK_STARTED: bool = Field(default=True, alias="task_track_started")
    CELERY_RESULT_PERSISTENT: bool = Field(default=True, alias="result_persistent")

    POSTGRES_URL_MASTER: str
    POSTGRES_URL_SLAVE: str
    POSTGRES_URL_ELAMBIC: str
    PORT: str
    PREFIX_URL: Optional[str] = Field(default="/v1/admin")
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    ALGORITHM: str
    SELF_URL: str = ""
    API_KEY: str = ""
    ACCOUNT_SID: str = ""
    AUTH_TOKEN: str = ""
    S3_BUCKET: str
    S3_KEY: str
    S3_SECRET: str
    REGION: str
    S3_ENDPOINT: str
    BOT_SERVICE_URL: str = ""


config = Config()


class ConnectionManager:
    def __init__(self):
        # {user_id: websocket}
        self.active_connections_online: Dict[int, WebSocket] = {}
        # {conversation_id: {user_id: websocket}}}
        self.active_rooms: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        if self.active_connections_online.get(client_id, None) is None:
            await websocket.accept()
            self.active_connections_online[client_id] = websocket

    def disconnect(self, *, client_id: int):
        if self.active_connections_online.get(client_id, None) is not None:
            _ = self.active_connections_online.pop(client_id)

    async def open_conversation(self, conversation_id: int, users: List[int]):
        if conversation_id not in self.active_rooms:
            self.active_rooms[conversation_id] = {}
        for user_id in users:
            user_online_socket = self.active_connections_online.get(user_id)
            if not user_online_socket:
                continue
            self.active_rooms[conversation_id][user_id] = user_online_socket

    async def send_message(
        self,
        conversation_id: int,
        user_send: int,
        message: Dict[str, Any],
    ):
        if self.active_rooms.get(conversation_id, None) is None:
            raise Exception("Conversation not found")
        user_in_rooms = self.active_rooms[conversation_id]
        for user_id, user_socket in user_in_rooms.items():
            if user_id == user_send:
                continue
            await user_socket.send_json(message)

    async def broadcast_system(self, message: Union[str, bytes, Any]):
        for websocket in self.active_connections_online.values():
            await websocket.send_json(message)

    def get_online_users(self) -> List[int]:
        return list(self.active_connections_online.keys())


connect_manager = ConnectionManager()
