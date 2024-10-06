from src.enum import MessageContentSchema
from src.repositories.message_repository import MessageRepository


class MessageHelper:
    def __init__(self, message_repository: MessageRepository):
        self.message_repository = message_repository

    async def get_messages_from_conversation(self, conversation_id: int):
        return await self.message_repository.get_messages_from_conversation(
            conversation_id
        )

    async def create_message(
        self,
        sender_id: int,
        conversation_id: int,
        reply_id: int | None,
        message: MessageContentSchema,
    ):
        return await self.message_repository.create_message(
            sender_id, conversation_id, reply_id, message
        )
