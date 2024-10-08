from collections import defaultdict

from sqlalchemy import exists, func, select
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import (
    catch_error_repository,
    exception_handler,
)
from src.core.exception import BadRequest
from src.enum import ErrorCode
from src.models.conversation_model import ConversationModel, ConversationUserModel
from src.models.user_model import UserModel
from src.schema.conversation_schema import RequestGetAllConversationSchema


class ConversationRepoitory(PostgresRepository[ConversationModel]):

    @catch_error_repository
    async def create_conversation(self, user_create: int, participant_id: int):
        user_exist = select(exists().where(UserModel.id == participant_id))
        result_user_exist = await self.session.execute(user_exist)
        data = result_user_exist.scalar()
        if not data:
            raise BadRequest(
                error_code=ErrorCode.BAD_REQUEST.name,
                errors={"message": "Not found user you want to create conversation"},
            )

        query_conversation = (
            select(ConversationModel)
            .join(ConversationUserModel)
            .filter(ConversationUserModel.user_id.in_([user_create, participant_id]))
            .group_by(ConversationModel.id)
            .having(func.count(ConversationUserModel.user_id) == 2)
        )
        result = await self.session.execute(query_conversation)

        conversation_model = result.scalar_one_or_none()

        if conversation_model:
            return {"conversation_id": conversation_model.id}
        # create new conversation id not exist
        new_conversation = ConversationModel()
        self.session.add(new_conversation)
        new_conversation.users.append(ConversationUserModel(user_id=user_create))
        new_conversation.users.append(ConversationUserModel(user_id=participant_id))
        await self.session.commit()
        return {"conversation_id": new_conversation.id}

    @exception_handler
    async def get_conversation(
        self, user_id: int, query_params: RequestGetAllConversationSchema
    ):
        query_conversation = (
            select(ConversationModel)
            .join(ConversationUserModel)
            .where(ConversationUserModel.user_id == user_id)
            .options(joinedload(ConversationModel.messages))
        )
        result_query = await self.session.execute(query_conversation)

        data_result_qurey = result_query.unique().scalars().all()

        items = []
        for item in data_result_qurey:
            data_dict = defaultdict()
            latest_message = item.latest_message
            data_dict.update(
                {
                    "conversation_id": item.id,
                    "latest_message": (
                        latest_message.as_dict if latest_message else None
                    ),
                }
            )
            items.append(data_dict)
        return items

    async def get_users_from_conversation(self, conversation_id: int):
        query_conversation = select(ConversationUserModel.user_id).where(
            ConversationUserModel.conversation_id == conversation_id
        )
        result_query = await self.session.execute(query_conversation)
        data_result_query = result_query.scalars().all()
        return data_result_query
