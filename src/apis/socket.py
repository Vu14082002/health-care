from typing import Any
from venv import logger

import jwt
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from src.config import config, connect_manager
from src.core.exception import Forbidden,BaseException
from src.enum import ErrorCode
from src.factory import Factory


class ValidateJsonWebToken:
    def __init__(self) -> None:
        self.access_key = config.ACCESS_TOKEN
        self.refresh_key = config.ACCESS_TOKEN
        self.algorithm = config.ALGORITHM

    async def validate(self, _authorization: str):
        _token = ""
        try:
            if not _authorization:
                raise
            _type, _token = _authorization.split()

            if _type.lower() != "bearer":
                raise
            _decode = jwt.decode(
                _token, key=self.access_key, algorithms=[self.algorithm]
            )
            _payload = _decode.get("payload", {})
            return _payload
        except jwt.exceptions.ExpiredSignatureError:
            raise Forbidden(
                msg="Token is expired", error_code=ErrorCode.TOKEN_EXPIRED.name
            )
        except Exception as e:
            logger.debug(e)
            raise Forbidden(msg="Authen Fail", error_code=ErrorCode.AUTHEN_FAIL.name)


validate_helper = ValidateJsonWebToken()


class OnlineUser(WebSocketEndpoint):
    encoding = "json"

    # {"conversation_id": 1}
    async def on_connect(self, websocket: WebSocket):
        try:
            authorization = websocket.headers.get("authorization")
            if authorization is None:
                await websocket.close(code=1008)
                return
            auth: dict[str, Any] = await validate_helper.validate(authorization)  # type: ignore
            user_id: int | None = auth.get("id")
            if not user_id:
                await websocket.close(code=1008)
                return
            await connect_manager.connect_online(websocket, user_id)
        except Exception as e:
            logger.error(e)
            await websocket.send_json({"message": "Can't connect"})
            await websocket.close(code=1008)

    async def on_receive(self, websocket: WebSocket, data):
        pass

    async def on_disconnect(self, websocket: WebSocket, close_code):  # type: ignore
        try:
            _ = await connect_manager.disconnect_user_online(client_id=1)
        except Exception as e:
            logger.error(e)
            await websocket.close(code=1008)


class OpenConversation(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket):
        try:
            authorization = websocket.headers.get("authorization")
            conversation_id = websocket.headers.get("conversation_id", None)
            if authorization is None:
                await websocket.close(code=1008)
                return
            if conversation_id is None:
                await websocket.close(code=1008)
                return
            auth: dict[str, Any] = await validate_helper.validate(authorization)  # type: ignore
            user_id: int | None = auth.get("id")
            if not user_id:
                await websocket.close(code=1008)
                return

            # logic open conversation
            conversation_helper = await Factory().get_conversation_helper()
            users_id = await conversation_helper.get_users_from_conversation(
                int(conversation_id)
            )
            await connect_manager.open_conversation(
                websocket, int(conversation_id), users_id, user_id=user_id
            )
            await websocket.send_json({"message": "open conversation success"})
            print(connect_manager.active_rooms)
        except Exception as e:
            logger.error(e)
            await websocket.send_json({"message": "Can't connect"})
            await websocket.close(code=1008)

    async def on_receive(self, websocket: WebSocket, data):
        pass

    async def on_disconnect(self, websocket: WebSocket, close_code):  # type: ignore
        try:
            authorization = websocket.headers.get("authorization")
            if authorization is None:
                await websocket.close(code=1008)
                return
            auth: dict[str, Any] = await validate_helper.validate(authorization)  # type: ignore
            user_id: int | None = auth.get("id", None)
            if not user_id:
                await websocket.close(code=1008)
                return
            _ = await connect_manager.close_conversation(user_id == user_id)
        except Exception as e:
            logger.error(e)
            await websocket.close(code=1008)


class MessageSocket(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket):  # type: ignore
        try:
            await websocket.accept()
            authorization = websocket.headers.get("authorization")
            if authorization is None:
                await websocket.close(code=1008)
                return
            await websocket.send_json({"message": "message ws connected"})
        except Exception as e:
            logger.error(e)
            await websocket.send_json({"message": "message ws can't connect"})
            await websocket.close(code=1008)

    async def on_receive(self, websocket: WebSocket, data):
        try:
            print("Vao day")
            authorization = websocket.headers.get("authorization")
            if authorization is None:
                await websocket.close(code=1008)
            auth: dict[str, Any] = await validate_helper.validate(authorization)  # type: ignore
            user_id: int = auth.get("id", None)
            if user_id is None:
                await websocket.close(code=1008)
            conversation_id: int | None = data.get("conversation_id", None)
            if conversation_id is None:
                raise Exception("conversation_id is required")
            await connect_manager.send_message(
                conversation_id=conversation_id,
                user_send=user_id,
                message=data,
            )  # type: ignore
        except Exception as e:
            logger.error(e)
            await websocket.send_json({"message": f"{e}"})
            await websocket.close(code=1008)

    async def on_disconnect(self, websocket: WebSocket, close_code):  # type: ignore
        try:
            authorization = websocket.headers.get("authorization")
            if authorization is None:
                await websocket.close(code=1008)
                return
            auth: dict[str, Any] = await validate_helper.validate(authorization)  # type: ignore
            user_id: int | None = auth.get("id", None)
            if not user_id:
                await websocket.close(code=1008)
                return
            _ = connect_manager.disconnect(client_id=user_id)
        except Exception as e:
            logger.error(e)
            await websocket.close(code=1008)
