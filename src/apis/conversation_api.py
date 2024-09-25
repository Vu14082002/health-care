import logging

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode
from src.factory import Factory
from src.schema.conversation_schema import RequestCreateConvertsationSchema


class ConversationApi(HTTPEndpoint):

    async def get(self, auth: JsonWebToken):
        try:
            conversation_service = await Factory().get_conversation_helper()
            conversation = await conversation_service.get_conversation(auth.get("id"))
            return conversation
        except (BadRequest, Forbidden, InternalServer) as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )

    async def post(self, form_data: RequestCreateConvertsationSchema, auth: JsonWebToken):
        try:
            if auth.get("id") == form_data.participant_id:
                raise BadRequest(
                    error_code=ErrorCode.BAD_REQUEST.name,
                    errors={"message": "You can not create conversation with yourself"},
                )
            conversation_service = await Factory().get_conversation_helper()
            conversation = await conversation_service.create_conversation(
                user_create=auth.get("id"), participant_id=form_data.participant_id
            )
            return conversation
        except (BadRequest, Forbidden, InternalServer) as e:
            raise e
        except Exception as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )