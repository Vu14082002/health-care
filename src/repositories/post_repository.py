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
        is_exists = await self._is_post_by_id(post_id)
        if is_exists is False:
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
        data = result_insert_data.unique().scalars().first()
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
        query_statment = select(PostModel).where(PostModel.id == post_id)
        result = await self.session.execute(query_statment)
        post = result.unique().scalars().first()
        if post is None:
            raise BadRequest(
                error_code=ErrorCode.NOT_FOUND.name,
                errors=({"message": "post not found"}),
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
        for comment in data_comment:
            user_comment = comment.user.patient
            if user_comment is None:
                user_comment = comment.user.doctor
            # FIXME: user_comment is None
            if user_comment is None:
                user_comment = {
                    "id": comment.user.id,
                    "email": "admin@gmail.com",
                    "first_name": "admin",
                    "last_name": "",
                }
            exclue_fields = [
                "certification",
                "verify_status",
                "is_local_person",
                "diploma",
                "type_of_disease",
                "hopital_address_work",
                "address",
                "description",
                "license_number",
                "education",
                "account_number",
                "bank_name",
                "beneficiary_name",
                "branch_name",
                "created_at",
                "updated_at",
                "is_deleted",
            ]
            user_comment = (
                {
                    key: value
                    for key, value in user_comment.as_dict.items()
                    if key not in exclue_fields
                }
                if not isinstance(user_comment, dict)
                else user_comment
            )
            comments.append(
                {
                    **comment.as_dict,
                    "created_at": datetime.fromtimestamp(
                        comment.created_at, timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "user": user_comment,
                }
            )
        await self.session.commit()
        return {
            **post.as_dict,
            "comments": comments,
        }
