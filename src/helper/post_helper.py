from typing import Any

from src.core.decorator.exception_decorator import catch_error_helper
from src.enum import MessageContentSchema
from src.repositories.post_repository import PostRepository


class PostHelper:
    def __init__(self, post_repository: PostRepository) -> None:
        self.post_repository = post_repository

    @catch_error_helper(message=None)
    async def create_post_helper(
        self, auth_id: int, title: str, content_schema: MessageContentSchema
    ):
        # business logic
        data = await self.post_repository.create_post_repository(
            auth_id, title, content_schema
        )
        return data

    @catch_error_helper(message=None)
    async def update_post_helper(
        self,
        auth_id: int,
        post_id: int,
        title: str | None,
        content_schema: MessageContentSchema | None,
    ):
        data = await self.post_repository.update_post_repository(
            auth_id, post_id, title, content_schema
        )
        return data

    @catch_error_helper(message=None)
    async def add_comment_helper(
        self, auth_id: int, post_id: int, content_schema: MessageContentSchema
    ):
        data = await self.post_repository.add_comment_repository(
            auth_id, post_id, content_schema
        )
        return data

    @catch_error_helper(message=None)
    async def update_comment_helper(
        self, auth_id: int, comment_id: int, content_schema: MessageContentSchema
    ):
        data = await self.post_repository.update_comment_repository(
            auth_id, comment_id, content_schema
        )
        return data

    @catch_error_helper(message=None)
    async def get_post_helper(self, query: dict[str, Any]):
        data = await self.post_repository.get_post_repository(query)
        return data

    @catch_error_helper(message=None)
    async def get_post_by_id_helper(self, post_id: int):
        data = await self.post_repository.get_post_repository_by_id(post_id)
        return data

    @catch_error_helper(message=None)
    async def delete_post_helper(self, post_id: int):
        data = await self.post_repository.delete_post_repository( post_id)
        return data

    @catch_error_helper(message=None)
    async def delete_comment_helper(self, comment_id: int, auth_comment_id:int | None = None):
        data = await self.post_repository.delete_comment_repository(comment_id, auth_comment_id)
        return data
