import logging as log

from sqlalchemy import exists, func, select
from sqlalchemy.orm import joinedload

from src.core.database.postgresql import PostgresRepository
from src.core.decorator.exception_decorator import catch_error_repository
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode
from src.models.conversation_model import (ConversationModel,
                                           ConversationUserModel)
from src.models.user_model import UserModel


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
            return {"message": "ok"}
        new_conversation = ConversationModel()
        self.session.add(new_conversation)
        new_conversation.users.append(
            ConversationUserModel(user_id=user_create))
        new_conversation.users.append(
            ConversationUserModel(user_id=participant_id))
        await self.session.commit()
        return {"message": "ok"}

    async def get_conversation(self, user_id: int):
        try:
            query_conversation = (
                select(ConversationModel)
                .join(ConversationUserModel)
                .filter(ConversationUserModel.user_id == user_id)
                .options(joinedload(ConversationModel.users))
                .options(joinedload(ConversationModel.messages))
            )
            result = await self.session.execute(query_conversation)
            conversation = result.scalars().all()
            return conversation
        except (BadRequest, InternalServer) as e:
            await self.session.rollback()
            raise e
        except Exception as e:
            log.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={
                    "message": "Error when execute get conversation ,please try again later"
                },
            )
