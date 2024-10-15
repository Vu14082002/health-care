import logging

from src.core.decorator.exception_decorator import catch_error_helper
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.repositories.conversation_repository import ConversationRepoitory
from src.schema.conversation_schema import RequestGetAllConversationSchema


class ConversationHelper:
    def __init__(self, conversation_repository: ConversationRepoitory):
        self.conversation_repository = conversation_repository

    @catch_error_helper(message=None)
    async def create_conversation(self, user_create: int, appointment_id: int):
        conversation = await self.conversation_repository.create_conversation(
            user_create, appointment_id
        )
        return conversation

    @catch_error_helper(message=None)
    async def get_conversation(
        self, user_id: int, query_params: RequestGetAllConversationSchema
    ):
        conversation = await self.conversation_repository.get_conversation(
            user_id, query_params
        )
        return conversation

    @catch_error_helper(message=None)
    async def get_users_from_conversation(self, conversation_id: int):
        users = await self.conversation_repository.get_users_from_conversation(
            conversation_id
        )
        return users
