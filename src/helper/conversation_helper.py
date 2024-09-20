from src.core.exception import BadRequest, InternalServer
from src.repositories.conversation_repository import ConversationRepoitory


class ConversationHelper:
    def __init__(self, conversation_repository: ConversationRepoitory):
        self.conversation_repository = conversation_repository
