from typing import Any

from src.core.decorator.exception_decorator import catch_error_helper
from src.enum import MessageContentSchema
from src.repositories.post_repository import PostRepository


class PostHelper:
    def __init__(self, post_repository: PostRepository) -> None:
        self.post_repository = post_repository

    @catch_error_helper(
        "Server error when handling business logic on create post,pls try later"
    )
    async def create_post_helper(
        self, auth_id: int, title: str, content_schema: MessageContentSchema
    ):
        # business logic
        data = await self.post_repository.create_post_repository(
            auth_id, title, content_schema
        )
        return data

    @catch_error_helper(
        "Server error when handling business logic on add commnent this post ,pls try later"
    )
    async def add_comment_helper(
        self, auth_id: int, post_id: int, content_schema: MessageContentSchema
    ):
        data = await self.post_repository.add_comment_repository(
            auth_id, post_id, content_schema
        )
        return data

    @catch_error_helper(
        "Server error when handling business logic on get posts ,pls try later"
    )
    async def get_post_helper(self, query: dict[str, Any]):
        data = await self.post_repository.get_post_repository(query)
        return data

    @catch_error_helper(
        "Server error when handling business logic on get post by id ,pls try later"
    )
    async def get_post_by_id_helper(self, post_id: int):
        data = await self.post_repository.get_post_repository_by_id(post_id)
        return data