from src.core.decorator.exception_decorator import catch_error_helper
from src.enum import MessageContentSchema
from src.repositories.message_repository import MessageRepository


class MessageHelper:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def get_messages_from_conversation(self, conversation_id: int):
        return await self.message_repository.get_messages_from_conversation(
            conversation_id
        )

    @catch_error_helper(message=None)
    async def create_message(
        self,
        sender_id: int,
        conversation_id: str,
        reply_id: int | None,
        message: MessageContentSchema,
        first_name: str | None,
        last_name: str | None,
        avatar: str | None,
        phone_number: str | None,
    ):
        return await self.message_repository.create_message(
            sender_id,
            conversation_id,
            reply_id,
            message,
            first_name,
            last_name,
            avatar,
            phone_number,
        )
