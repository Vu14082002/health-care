import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal

from sqlalchemy import asc, desc, exists, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.database.postgresql.repository import PostgresRepository
from src.core.decorator.exception_decorator import (
    catch_error_repository,
)
from src.core.exception import BadRequest, InternalServer
from src.enum import ErrorCode, MessageContentSchema
from src.models.post_model import CommentModel, PostModel
from src.models.user_model import UserModel


class PostRepository(PostgresRepository[PostModel]):

    def __init__(self, model: PostModel, db_session: AsyncSession):
        super().__init__(model, db_session)

    @catch_error_repository(message=None)
    async def create_post_repository(
        self, auth_id: int, title: str, content_schema: MessageContentSchema
    ):
        insert_statment = (
            insert(PostModel)
            .values(
                {
                    "author_id": auth_id,
                    "title": title,
                    "content": content_schema.model_dump(),
                }
            )
            .returning(PostModel)
        )
        result_insert_statment = await self.session.execute(insert_statment)
        data_insert_statment = result_insert_statment.scalars().first()
        if data_insert_statment is None:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors=({"message": ErrorCode.msg_server_error.value}),
            )
        await self.session.commit()
        return data_insert_statment.as_dict

    @catch_error_repository(message=None)
    async def add_comment_repository(
        self, auth_id: int, post_id: int, content_schema: MessageContentSchema
    ):
        is_exists = await self._is_post_by_id(post_id)
        if is_exists is False:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": ErrorCode.msg_post_not_found.value}),
            )
        insert_data = (
            insert(CommentModel)
            .values(
                {
                    "user_id": auth_id,
                    "post_id": post_id,
                    "content": content_schema.model_dump(),
                }
            )
            .returning(CommentModel)
        )
        result_insert_data = await self.session.execute(insert_data)
        data = result_insert_data.unique().scalars().first()
        if data is None:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors=({"message": ErrorCode.msg_server_error.value}),
            )
        await self.session.commit()

        result_user_comment = await self.session.execute(
            select(UserModel).where(UserModel.id == auth_id)
        )
        data_user_comment = result_user_comment.scalar_one_or_none()
        if data_user_comment is None:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors=({"message": ErrorCode.msg_server_error.value}),
            )
        user_comment = (
            data_user_comment.patient
            or data_user_comment.doctor
            or data_user_comment.staff
        )
        include_fields = ["id", "email", "first_name", "last_name", "avatar"]
        data = {
            **data.as_dict,
            "created_at": datetime.fromtimestamp(
                data.created_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.fromtimestamp(
                data.updated_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                key: value
                for key, value in user_comment.as_dict.items()
                if key in include_fields
            },
        }
        return data

    @catch_error_repository(message=None)
    async def update_comment_repository(
        self, auth_id: int, comment_id: int, content_schema: MessageContentSchema
    ):
        comment_statment = select(CommentModel).where(CommentModel.id == comment_id)
        result_comment_statment = await self.session.execute(comment_statment)
        comment = result_comment_statment.unique().scalars().first()
        if not comment:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": "comment not found"}),
            )
        if comment.user_id != auth_id:
            raise BadRequest(
                error_code=ErrorCode.FORBIDDEN.name,
                errors=({"message": "you can't update this comment"}),
            )
        comment.content = content_schema.model_dump()
        await self.session.commit()
        user_comment = comment.user.patient or comment.user.doctor or comment.user.staff
        include_fields = ["id", "email", "first_name", "last_name", "avatar"]
        data = {
            **comment.as_dict,
            "created_at": datetime.fromtimestamp(
                comment.created_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.fromtimestamp(
                comment.updated_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                key: value
                for key, value in user_comment.as_dict.items()
                if key in include_fields
            },
        }
        return data

    @catch_error_repository(message=None)
    async def update_post_repository(
        self,
        auth_id: int,
        post_id: int,
        title: str | None,
        content_schema: MessageContentSchema | None,
    ):
        post_statment = select(PostModel).where(PostModel.id == post_id, PostModel.is_deleted == False)
        result_post_statment = await self.session.execute(post_statment)
        post = result_post_statment.unique().scalars().first()
        if not post:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": ErrorCode.msg_post_not_found.value}),
            )
        # if post.author_id != auth_id:
        #     raise BadRequest(
        #         error_code=ErrorCode.FORBIDDEN.name,
        #         errors=({"message": "you can't update this post"}),
        #     )
        if title:
            post.title = title
        if content_schema:
            post.content = content_schema.model_dump()
        self.session.add(post)
        await self.session.commit()
        return post.as_dict

    async def _is_post_by_id(self, post_id: int):
        check_statment = select(exists().where(PostModel.id == post_id, PostModel.is_deleted == False))
        result_check_statment = await self.session.execute(check_statment)
        return result_check_statment.scalar_one()

    @catch_error_repository(message=None)
    async def get_post_repository(self, query: Dict[str, Any]):
        title: str = query.get("title", None)
        current_page: int = query.get("current_page", 1)
        page_size: int = query.get("page_size", 10)
        offset_value = (current_page - 1) * page_size
        sort_by: Literal["created_at", "viewed"] = query.get("sort_by", "created_at")
        sort_order: str = query.get("sort_order", "desc")

        query_statement = select(PostModel).where(PostModel.is_deleted == False)

        if title:
            query_statement = query_statement.where(PostModel.title.ilike(f"%{title}%"))

        total_posts_statement = (
            select(func.count(PostModel.id))
            .select_from(PostModel)
            .where(PostModel.is_deleted == False)
        )
        if title:
            total_posts_statement = total_posts_statement.where(
                PostModel.title.ilike(f"%{title}%")
            )

        result_total_posts = await self.session.execute(total_posts_statement)
        total_posts = result_total_posts.scalar_one()

        if sort_order == "asc":
            query_statement = query_statement.order_by(asc(getattr(PostModel, sort_by)))
        else:
            query_statement = query_statement.order_by(
                desc(getattr(PostModel, sort_by))
            )

        query_statement = (
            query_statement.options(joinedload(PostModel.comments))
            .offset(offset_value)
            .limit(page_size)
        )

        result = await self.session.execute(query_statement)
        posts = result.unique().scalars().all()

        items = []
        for post in posts:
            include_fields = ["id", "email", "first_name", "last_name", "avatar"]
            auth_post = post.author
            user = auth_post.patient or auth_post.doctor or auth_post.staff
            user = {
                key: value
                for key, value in user.as_dict.items()
                if key in include_fields
            }
            item = {
                "user": user,
                **post.as_dict,
                "comment": post.get_size_comments,
                "created_at": datetime.fromtimestamp(
                    post.created_at, timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.fromtimestamp(
                    post.updated_at, timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }

            items.append(item)

        return {
            "items": items,
            "current_page": current_page,
            "page_size": page_size,
            "total_page": math.ceil(total_posts / page_size),
        }

    @catch_error_repository(message=None)
    async def get_post_repository_by_id(self, post_id: int):
        query_statment = select(PostModel).where(PostModel.id == post_id, PostModel.is_deleted == False)
        result = await self.session.execute(query_statment)
        post = result.unique().scalars().first()
        if post is None:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": ErrorCode.msg_post_not_found.value}),
            )
        # plus view
        post.viewed += 1
        self.session.add(post)
        comment_select = (
            select(CommentModel)
            .where(CommentModel.post_id == post_id)
            .options(joinedload(CommentModel.user))
            .order_by(desc(CommentModel.created_at))
        )
        result_commnet = await self.session.execute(comment_select)
        data_comment = result_commnet.unique().scalars().all()
        comments = []
        include_fields = ["id", "email", "first_name", "last_name", "avatar"]
        for comment in data_comment:
            user_comment = (
                comment.user.patient or comment.user.doctor or comment.user.staff
            )
            user_comment = {
                key: value
                for key, value in user_comment.as_dict.items()
                if key in include_fields
            }
            comments.append(
                {
                    **comment.as_dict,
                    "created_at": datetime.fromtimestamp(
                        comment.created_at, timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.fromtimestamp(
                        comment.updated_at, timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "user": user_comment,
                }
            )
        await self.session.commit()
        auth_data =post.author
        auth_data = auth_data.patient or auth_data.doctor or auth_data.staff
        auth_custom = {
                "auth_id": auth_data.id,
                "email": auth_data.email,
                "first_name": auth_data.first_name,
                "last_name": auth_data.last_name,
                "avatar": auth_data.avatar,
        }
        return {
            **post.as_dict,
            **auth_custom,
            "created_at": datetime.fromtimestamp(
                post.created_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.fromtimestamp(
                post.updated_at, timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "comments": comments,
        }

    @catch_error_repository(message=None)
    async def delete_post_repository(self,post_id: int):
        post_statment = select(PostModel).where(PostModel.id == post_id, PostModel.is_deleted == False)
        result_post_statment = await self.session.execute(post_statment)
        post = result_post_statment.unique().scalars().first()
        if not post:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": ErrorCode.msg_post_not_found.value}),
            )
        post.is_deleted = True
        await self.session.commit()
        return {
            "message": ErrorCode.msg_delete_post_successfully.value
        }
    @catch_error_repository(message=None)
    async def delete_comment_repository(self, comment_id: int, auth_comment_id: int | None = None):
        comment_statment = select(CommentModel).where(CommentModel.id == comment_id)
        result_comment_statment = await self.session.execute(comment_statment)
        comment = result_comment_statment.unique().scalars().first()
        if not comment:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": ErrorCode.msg_comment_not_found.value}),
            )
        if auth_comment_id is not None and comment.user_id != auth_comment_id:
            raise BadRequest(
                error_code=ErrorCode.FORBIDDEN.name,
                errors=({"message": ErrorCode.msg_can_not_delete_comment.value}),
            )
        await self.session.delete(comment)
        await self.session.commit()
        return {
            "message": ErrorCode.msg_delete_comment_successfully.value
        }
