import logging

from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.repositories.conversation_repository import ConversationRepoitory
from src.schema.conversation_schema import RequestGetAllConversationSchema


class ConversationHelper:
    def __init__(self, conversation_repository: ConversationRepoitory):
        self.conversation_repository = conversation_repository

    async def create_conversation(self, user_create: int, participant_id: int):
        try:
            conversation = await self.conversation_repository.create_conversation(
                user_create, participant_id
            )
            return conversation
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except (Exception, InternalServer) as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )

    async def get_conversation(
        self, user_id: int, query_params: RequestGetAllConversationSchema
    ):
        try:
            conversation = await self.conversation_repository.get_conversation(
                user_id, query_params
            )
            return conversation
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except (Exception, InternalServer) as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )

    async def get_users_from_conversation(self, conversation_id: int):
        try:
            users = await self.conversation_repository.get_users_from_conversation(
                conversation_id
            )
            return users
        except (BadRequest, InternalServer) as e:
            logging.error(e)
            raise e
        except (Exception, InternalServer) as e:
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Server currently unable to handle this request,please try again later"
                },
            )
