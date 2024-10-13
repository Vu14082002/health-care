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


class PostRepository(PostgresRepository[PostModel]):

    def __init__(self, model: PostModel, db_session: AsyncSession):
        super().__init__(model, db_session)

    @catch_error_repository(
        message="Server error when handling create post, pls try later"
    )
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

    @catch_error_repository(
        "Server error when handling add comment this post, pls try later"
    )
    async def add_comment_repository(
        self, auth_id: int, post_id: int, content_schema: MessageContentSchema
    ):

        if self._is_post_by_id(post_id) is False:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": "post not found"}),
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
        data = result_insert_data.scalar_one_or_none()
        if data is None:
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors=({"message": ErrorCode.msg_server_error.value}),
            )
        await self.session.commit()
        return data.as_dict

    async def _is_post_by_id(self, post_id: int):
        check_statment = select(exists().where(PostModel.id == post_id))
        result_check_statment = await self.session.execute(check_statment)
        return result_check_statment.scalar_one()

    @catch_error_repository("Server error when handling get post, please try later")
    async def get_post_repository(self, query: Dict[str, Any]):
        title: str = query.get("title", None)
        current_page: int = query.get("current_page", 1)
        page_size: int = query.get("page_size", 10)
        offset_value = (current_page - 1) * page_size
        sort_by: Literal["created_at", "viewed"] = query.get("sort_by", "created_at")
        sort_order: str = query.get("sort_order", "desc")

        query_statement = select(PostModel)

        if title:
            query_statement = query_statement.where(PostModel.title.ilike(f"%{title}%"))

        total_posts_statement = select(func.count(PostModel.id)).select_from(PostModel)
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

        items = [
            {
                **post.as_dict,
                "comment": post.get_size_comments,
                "created_at": datetime.fromtimestamp(
                    post.created_at, timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
            }
            for post in posts
        ]

        return {
            "items": items,
            "current_page": current_page,
            "page_size": page_size,
            "total_page": math.ceil(total_posts / page_size),
        }

    @catch_error_repository("Server error when handling get post, pls try later")
    async def get_post_repository_by_id(self, post_id: int):
        query_statment = (
            select(PostModel)
            .where(PostModel.id == post_id)
            .options(joinedload(PostModel.comments))
            .order_by(PostModel.created_at.desc(), PostModel.comments.created_at.desc())
        )
