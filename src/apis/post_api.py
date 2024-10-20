import logging

from starlette.datastructures import UploadFile
from starlette.requests import Request

from src.core.endpoint import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, MessageContentSchema, Role
from src.factory import Factory
from src.helper.s3_helper import S3Service
from src.schema.post_schema import (
    RequestCreateComment,
    RequestCreatePostSchema,
    RequestDeleteCommentSchema,
    RequestDeletePostSchema,
    RequestGetAllPostSchema,
    RequestGetPostByIdSchema,
    RequestUpdateComment,
    RequestUpdatePostSchema,
)


class GetPostUserApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetAllPostSchema):
        try:
            post_helper = await Factory().get_post_helper()
            result = await post_helper.get_post_helper(query=query_params.model_dump())
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )
class CreatePostApi(HTTPEndpoint):

    # async def get(self, query_params: RequestGetAllPostSchema):
    #     try:
    #         post_helper = await Factory().get_post_helper()
    #         result = await post_helper.get_post_helper(query=query_params.model_dump())
    #         return result
    #     except Exception as e:
    #         if isinstance(e, BaseException):
    #             raise e
    #         logging.error(e)
    #         raise InternalServer(
    #             error_code=ErrorCode.SERVER_ERROR.name,
    #             errors={"message": ErrorCode.msg_server_error.value},
    #         )

    async def post(
        self, request: Request, form_data: RequestCreatePostSchema, auth: JsonWebToken
    ):
        """
        this api is used to create post ,  only admin can create post
        """
        try:
            if auth.get("role") != Role.ADMIN.value:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            if all(
                field is None
                for field in [form_data.content, form_data.media, form_data.images]
            ):
                raise BadRequest(
                    error_code=ErrorCode.VALIDATION_ERROR.name,
                    errors={"message": ErrorCode.msg_content_message_required.value},
                )
            s3_service = S3Service()
            media = None
            images = None
            content = form_data.content
            if form_data.media:
                if isinstance(form_data.media, UploadFile):
                    upload_file: UploadFile = form_data.media
                    media = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.media, str) and form_data.media.startswith(
                    "http"
                ):
                    media = form_data.media
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )
            form_request = await request.form()
            images = []
            images_form = form_request.getlist("images")
            for image in images_form:
                if isinstance(image, UploadFile):
                    upload_file: UploadFile = image
                    image = await s3_service.upload_file_from_form(upload_file)
                    images.append(image)
                elif isinstance(image, str) and image.startswith("http"):
                    images.append(image)
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )

            content_schema = MessageContentSchema(
                media=media, images=images, content=content
            )
            post_helper = await Factory().get_post_helper()
            result = await post_helper.create_post_helper(
                auth_id=auth.get("id"),
                title=form_data.title,
                content_schema=content_schema,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    async def put(
        self, request: Request, form_data: RequestUpdatePostSchema, auth: JsonWebToken
    ):
        '''
        this api is used to update post, only admin can update post
        '''
        try:
            if auth.get("role") != Role.ADMIN.value:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            if all(
                field is None
                for field in [
                    form_data.content,
                    form_data.media,
                    form_data.images,
                    form_data.title,
                ]
            ):
                raise BadRequest(
                    error_code=ErrorCode.VALIDATION_ERROR.name,
                    errors={
                        "message": ErrorCode.msg_content_message_or_title_required.value
                    },
                )
            s3_service = S3Service()
            media = None
            images = None
            content = form_data.content
            if form_data.media:
                if isinstance(form_data.media, UploadFile):
                    upload_file: UploadFile = form_data.media
                    media = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.media, str) and form_data.media.startswith(
                    "http"
                ):
                    media = form_data.media
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )
            form_request = await request.form()
            images = []
            images_form = form_request.getlist("images")
            for image in images_form:
                if isinstance(image, UploadFile):
                    upload_file: UploadFile = image
                    image = await s3_service.upload_file_from_form(upload_file)
                    images.append(image)
                if isinstance(image, str) and image.startswith("http"):
                    images.append(image)
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )

            content_schema = (
                MessageContentSchema(media=media, images=images, content=content)
                if (media or images or content)
                else None
            )
            post_helper = await Factory().get_post_helper()
            result = await post_helper.update_post_helper(
                auth_id=auth.get("id"),
                post_id=form_data.post_id,
                title=form_data.title,
                content_schema=content_schema,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    async def delete(self, form_data: RequestDeletePostSchema, auth: JsonWebToken):
        '''
        this api is used to delete post, only admin can delete post
        '''
        try:
            if auth.get("role") != Role.ADMIN.value:
                raise Forbidden(
                    error_code=ErrorCode.FORBIDDEN.name,
                    errors={"message": ErrorCode.msg_permission_denied.value},
                )
            post_helper = await Factory().get_post_helper()
            result = await post_helper.delete_post_helper(
                post_id=form_data.post_id
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )


class GetPostByIdApi(HTTPEndpoint):

    async def get(self, path_params: RequestGetPostByIdSchema):
        try:
            post_helper = await Factory().get_post_helper()
            result = await post_helper.get_post_by_id_helper(
                post_id=path_params.post_id
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )


class CommentApi(HTTPEndpoint):
    async def post(
        self, request: Request, form_data: RequestCreateComment, auth: JsonWebToken
    ):
        try:
            if all(
                field is None
                for field in [form_data.content, form_data.media, form_data.images]
            ):
                raise BadRequest(
                    error_code=ErrorCode.VALIDATION_ERROR.name,
                    errors={"message": ErrorCode.msg_content_message_required.value},
                )
            s3_service = S3Service()
            media = None
            images = None
            content = form_data.content
            if form_data.media:
                if isinstance(form_data.media, UploadFile):
                    upload_file: UploadFile = form_data.media
                    media = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.media, str) and form_data.media.startswith(
                    "http"
                ):
                    media = form_data.media
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )
            form_request = await request.form()
            images = []
            images_form = form_request.getlist("images")
            for image in images_form:
                if isinstance(image, UploadFile):
                    upload_file: UploadFile = image
                    image = await s3_service.upload_file_from_form(upload_file)
                    images.append(image)
                elif isinstance(image, str) and image.startswith("http"):
                    images.append(image)
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )

            content_schema = MessageContentSchema(
                media=media, images=images, content=content
            )
            post_helper = await Factory().get_post_helper()
            result = await post_helper.add_comment_helper(
                auth_id=auth.get("id"),
                post_id=form_data.post_id,
                content_schema=content_schema,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    async def put(
        self, request: Request, form_data: RequestUpdateComment, auth: JsonWebToken
    ):
        try:
            if all(
                field is None
                for field in [form_data.content, form_data.media, form_data.images]
            ):
                raise BadRequest(
                    error_code=ErrorCode.VALIDATION_ERROR.name,
                    errors={"message": ErrorCode.msg_content_message_required.value},
                )
            s3_service = S3Service()
            media = None
            images = None
            content = form_data.content
            if form_data.media:
                if isinstance(form_data.media, UploadFile):
                    upload_file: UploadFile = form_data.media
                    media = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.media, str) and form_data.media.startswith(
                    "http"
                ):
                    media = form_data.media
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )
            form_request = await request.form()
            images = []
            images_form = form_request.getlist("images")
            for image in images_form:
                if isinstance(image, UploadFile):
                    upload_file: UploadFile = image
                    image = await s3_service.upload_file_from_form(upload_file)
                    images.append(image)
                else:
                    raise BadRequest(
                        error_code=ErrorCode.VALIDATION_ERROR.name,
                        errors={"message": ErrorCode.msg_invalid_medical_record.value},
                    )

            content_schema = MessageContentSchema(
                media=media, images=images, content=content
            )
            post_helper = await Factory().get_post_helper()
            result = await post_helper.update_comment_helper(
                auth_id=auth.get("id"),
                comment_id=form_data.comment_id,
                content_schema=content_schema,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    async def delete(self, form_data: RequestDeleteCommentSchema, auth: JsonWebToken):
        try:

            is_admin = True if auth.get("role") == Role.ADMIN.value else False
            comment_id = form_data.comment_id
            auth_comment_id = auth.get("id") if not is_admin else None
            post_helper = await Factory().get_post_helper()
            result = await post_helper.delete_comment_helper(
                comment_id=comment_id,
                auth_comment_id=auth_comment_id,
            )
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(e)
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )
