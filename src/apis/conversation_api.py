import logging

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode
from src.factory import Factory
from src.schema.conversation_schema import (
    RequestCreateConvertsationSchema,
    RequestGetAllConversationSchema,
)


class ConversationApi(HTTPEndpoint):

    async def get(
        self, query_params: RequestGetAllConversationSchema, auth: JsonWebToken
    ):
        try:
            conversation_service = await Factory().get_conversation_helper()
            conversation = await conversation_service.get_conversation(
                auth.get("id"), query_params
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

    async def post(
        self, form_data: RequestCreateConvertsationSchema, auth: JsonWebToken
    ):
        try:
            conversation_service = await Factory().get_conversation_helper()
            conversation = await conversation_service.create_conversation(
                user_create=auth.get("id"), appointment_id=form_data.appointment_id
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
