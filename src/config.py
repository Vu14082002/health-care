
from typing import Any, Dict, List, Optional, Union

from payos import PayOS
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
    SMTP_MAIL: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USERNAME: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = ""
    LINK_VERIFY_EMAIL: str = "localhost:8000/v1/admin/auth/verify-email"
    PAYOS_CLIENT_ID:str = ""
    PAYOS_API_KEY:str = ""
    PAYOS_CHECK_SUM:str = ""
    BASE_URL_CHAT_SERVICE: str = ""

config = Config()


payOsIns = PayOS(
    client_id=config.PAYOS_CLIENT_ID,
    api_key=config.PAYOS_API_KEY,
    checksum_key=config.PAYOS_CHECK_SUM,
)


class ConnectionManager:
    def __init__(self):
        self.active_connections_online: Dict[int, WebSocket] = {}
        self.active_rooms: Dict[int, Dict[int, WebSocket]] = {}

    # online logic
    async def connect_online(self, websocket: WebSocket, client_id: int):
        self.active_connections_online[client_id] = websocket
        await websocket.accept()
        await self.broadcast_system({"message": f"user {client_id} has been online"})

    async def disconnect_user_online(self, *, client_id: int):
        websocket = self.active_connections_online.pop(client_id, None)
        if websocket is not None:
            await self.broadcast_system(
                {"message": f"user {client_id} has been logged out"}
            )
            await websocket.close()

    # conversation logic
    async def open_conversation(
        self, websocket: WebSocket, conversation_id: int, users: List[int], user_id: int
    ):
        if self.active_rooms.get(conversation_id, None) is None:
            self.active_rooms[conversation_id] = {}
        self.active_rooms.get(conversation_id).update({user_id: websocket})  # type: ignore
        await websocket.accept()
        # for user_id in users:
        #     user_room = self.active_rooms[conversation_id]
        #     if user_room.get(user_id, None) is None:
        #         self.active_rooms[conversation_id][user_id] = websocket
        #         await websocket.accept()
        #     else:
        #         _ = self.active_rooms[conversation_id].pop(user_id)
        #         self.active_rooms[conversation_id][user_id] = websocket
        #         await websocket.accept()
        #         break

    async def close_conversation(self, user_id: int):
        for conversation_id, user_in_rooms in self.active_rooms.items():
            if user_id in user_in_rooms:
                _ = user_in_rooms.pop(user_id)
                if len(user_in_rooms) == 0:
                    _ = self.active_rooms.pop(conversation_id)

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
            _ = await user_socket.send_json(message)

    async def broadcast_system(self, message: Union[str, bytes, Any]):
        for websocket in self.active_connections_online.values():
            await websocket.send_json(message)

    def get_online_users(self) -> List[int]:
        return list(self.active_connections_online.keys())


connect_manager = ConnectionManager()
