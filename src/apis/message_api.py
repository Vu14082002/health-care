import logging

from starlette.datastructures import UploadFile

from src.core.endpoint import HTTPEndpoint
from src.core.exception import BadRequest, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, MessageContentSchema
from src.factory import Factory
from src.helper.s3_helper import S3Service
from src.schema.message_schema import (
    RequestCreateMessageSchema,
    RequestGetMessageSchema,
)


class MessageApi(HTTPEndpoint):
    async def get(self, query_params: RequestGetMessageSchema, auth: JsonWebToken):
        try:
            message_helper = await Factory().get_message_helper()
            result = await message_helper.get_messages_from_conversation(
                query_params.conversation_id
            )
            return result
        except Exception as e:
            logging.error(e)

    async def post(self, form_data: RequestCreateMessageSchema, auth: JsonWebToken):
        try:
            if all(
                item is None
                for item in [form_data.content, form_data.media, form_data.image]
            ):
                raise BadRequest(
                    error_code=ErrorCode.VALIDATION_ERROR.name,
                    errors={
                        "message": "At least one of content, media, or image must be provided"
                    },
                )
            sender_id = auth.get("id", None)
            if not sender_id:
                raise BadRequest(
                    msg="Invalid token", error_code=ErrorCode.AUTHEN_FAIL.name
                )
            s3_service = S3Service()
            media = None
            image = None
            content = form_data.content
            if form_data.media:
                if isinstance(form_data.media, UploadFile):
                    upload_file: UploadFile = form_data.media
                    media = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.media, bytes):
                    media = await s3_service.upload_file_from_bytes(
                        form_data.media, "media.mp4"
                    )
                else:
                    raise ValueError("media must be UploadFile or bytes")
                if media is None:
                    raise BadRequest(error_code=ErrorCode.S)
            # Upload image file if provided
            if form_data.image:
                if isinstance(form_data.image, UploadFile):
                    upload_file: UploadFile = form_data.image
                    await upload_file.seek(0)
                    image = await s3_service.upload_file_from_form(upload_file)
                elif isinstance(form_data.image, bytes):
                    image = await s3_service.upload_file_from_bytes(
                        form_data.image, "image.jpg"
                    )
                else:
                    raise ValueError("image must be UploadFile or bytes")
            message_content = MessageContentSchema(
                media=media, image=image, content=content
            )
            message_helper = await Factory().get_message_helper()
            result = await message_helper.create_message(
                sender_id=sender_id,
                conversation_id=form_data.conversation_id,
                reply_id=form_data.reply_id,
                message=message_content,
            )
            return result
        except (ValueError, BadRequest, InternalServer) as e:
            raise e
        except Exception as e:
            raise InternalServer(
                msg="Internal server error", error_code=ErrorCode.SERVER_ERROR.name
            ) from e
