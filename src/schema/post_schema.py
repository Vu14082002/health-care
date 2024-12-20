from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from src.enum import MsgEnumBase


class RequestGetPostByIdSchema(BaseModel):
    post_id: int = Field(..., title="Post id will get", examples=[1])

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RequestGetAllPostSchema(BaseModel):
    text_search: Optional[str] = Field(
        default=None,
        description="Search post by title",
    )
    current_page: int = Field(
        default=1, description="Page number to get, starting from 1", examples=[1]
    )
    page_size: int = Field(
        default=10, description="Number of items per page, default = 10", examples=[10]
    )
    sort_by: Literal["created_at", "viewed"] = Field(
        "created_at",
        description="sort post by created_at is default",
        examples=["created_at", "viewed"],
    )
    sort_order: Literal["asc", "desc"] = Field(
        default="desc",
        description="Order of sorting, default is descending",
        examples=["asc", "desc"],
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestCreatePostSchema(BaseModel):
    title: str = Field(
        ..., title="Title of the post", examples=["How to clean your skin"]
    )
    media: Optional[Any] = Field(
        default=None,
        description=MsgEnumBase.DES_MEDIA_FILE.value,
    )
    images: Optional[Any] = Field(
        default=None,
        description=MsgEnumBase.DES_MEDIA_FILE.value,
    )
    content: Optional[str] = Field(
        None,
        description=MsgEnumBase.DES_POST_CONTENT.value,
        examples=[MsgEnumBase.DES_POST_EXAMPLE.value],
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestUpdatePostSchema(BaseModel):
    post_id: int = Field(..., title="Post id will update", examples=[1])
    title: str | None = Field(
        None, title="Title of the post", examples=["How to clean your skin"]
    )
    media: Optional[Any] = Field(
        default=None,
        description="is video of post, and accept one file",
    )
    images: Optional[Any] = Field(
        default=None,
        description="is img of post and accept multiple files or url img",
    )
    content: Optional[str] = Field(
        None,
        description=MsgEnumBase.DES_POST_CONTENT.value,
        examples=[MsgEnumBase.DES_POST_EXAMPLE.value],
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestDeletePostSchema(BaseModel):
    post_id: int = Field(..., title="Post id will be delete", examples=[1])
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestCreateComment(BaseModel):
    post_id: int = Field(..., title="Post id will comment", examples=[1])

    media: Optional[Any] = Field(
        default=None,
        description="is video of post, and accept one file",
    )
    images: Optional[Any] = Field(
        default=None,
        description="is img of post and accept multiple files",
    )
    content: Optional[str] = Field(
        None,
        description=MsgEnumBase.DES_POST_CONTENT.value,
        examples=[MsgEnumBase.DES_POST_EXAMPLE.value],
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestUpdateComment(BaseModel):
    comment_id: int = Field(..., title="Comment id will update", examples=[1])
    media: Optional[Any] = Field(
        default=None,
        description="is video of post, and accept file or url video",
    )
    images: Optional[Any] = Field(
        default=None,
        description="is img of post and accept multiple files",
    )
    content: Optional[str] = Field(
        None,
        description=MsgEnumBase.DES_POST_CONTENT.value,
        examples=[MsgEnumBase.DES_POST_EXAMPLE.value],
    )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"


class RequestDeleteCommentSchema(BaseModel):
    comment_id: int = Field(..., description="Comment id will be delete, only this user can delete this comment, ADMIN have permiss to delete this comment ", examples=[1])
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        extra = "forbid"
