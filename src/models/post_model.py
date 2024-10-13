from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.postgresql.repository import Model
from src.enum import MessageContentSchema

if TYPE_CHECKING:
    from src.models.user_model import UserModel


class PostModel(Model):
    __tablename__ = "post"
    __table_args__ = (
        Index("idx_post_author_title", "author_id", "title"),
        Index("idx_post_author", "author_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[MessageContentSchema] = mapped_column(JSONB, nullable=False)
    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    author: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="posts",
        lazy="joined",
        passive_deletes=True,
    )
    comments: Mapped[List["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    viewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    @property
    def get_size_comments(self) -> int:
        return len(self.comments) if self.comments else 0


class CommentModel(Model):
    __tablename__ = "comment"
    __table_args__ = (
        Index("ix_comment_user_post", "user_id", "post_id"),
        Index("ix_comment_post_id", "post_id"),
    )
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    content: Mapped[MessageContentSchema] = mapped_column(JSONB, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("post.id", ondelete="CASCADE"),
        nullable=False,
    )
    post: Mapped["PostModel"] = relationship(
        "PostModel",
        back_populates="comments",
        lazy="joined",
        passive_deletes=True,
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="comment_posts", lazy="joined", passive_deletes=True
    )
