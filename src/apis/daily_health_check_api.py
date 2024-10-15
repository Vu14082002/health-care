import logging
from typing import List, Union

from starlette.datastructures import UploadFile
from starlette.requests import Request

from src.core import HTTPEndpoint
from src.core.exception import BadRequest, BaseException, Forbidden, InternalServer
from src.core.security.authentication import JsonWebToken
from src.enum import ErrorCode, ImageDailyHealthCheck, Role
from src.factory import Factory
from src.helper.daily_health_check_helper import DailyHealthCheckHelper
from src.helper.s3_helper import S3Service
from src.schema.daily_health_check_schema import (
    DailyHealthCheckSchema,
    RequestCreateHealthCheckSchema,
    RequestGetAllDailyHealthSchema,
)


class DailyDealthCheckApi(HTTPEndpoint):
    async def post(
        self,
        request: Request,
        form_data: RequestCreateHealthCheckSchema,
        auth: JsonWebToken,
    ):
        try:
            if not self._is_authorized(auth):
                return BadRequest(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            patient_id = self._get_patient_id(auth, form_data)
            if not patient_id:
                return BadRequest(
                    error_code=ErrorCode.INVALID_REQUEST.name,
                    errors={"message": "Id is required"},
                )

            form = await request.form()
            img_arr: List[Union[UploadFile, str]] = form.getlist("img_arr")
            images = await self._process_images(img_arr)

            health_check_schema = DailyHealthCheckSchema(
                appointment_id=form_data.appointment_id,
                patient_id=patient_id,
                temperature=form_data.temperature,
                assessment=form_data.assessment,
                describe_health=form_data.describe_health,
                link_image_data=images,
                date_create=form_data.date_create,
            )
            helper: DailyHealthCheckHelper = (
                await Factory().get_daily_health_check_helper()
            )
            result = await helper.create_daily_health_check(health_check_schema)
            return result
        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    async def get(
        self, query_params: RequestGetAllDailyHealthSchema, auth: JsonWebToken
    ):
        try:
            user_role = auth.get("role")
            if user_role not in [Role.ADMIN.name, Role.PATIENT.name, Role.DOCTOR.name]:
                return Forbidden(
                    error_code=ErrorCode.UNAUTHORIZED.name,
                    errors={
                        "message": ErrorCode.msg_permission_denied.value,
                    },
                )
            patient_id = (
                auth.get("id")
                if user_role == Role.PATIENT.name
                else query_params.patient_id
            )
            doctor_id = auth.get("id") if user_role == Role.DOCTOR.name else None
            if patient_id is None:
                raise BadRequest(
                    error_code=ErrorCode.INVALID_REQUEST.name,
                    errors={"message": "patient_id: patient is required"},
                )
            helper = await Factory().get_daily_health_check_helper()
            result = await helper.get_all_daily_health_check(query_params, doctor_id)
            return result

        except Exception as e:
            if isinstance(e, BaseException):
                raise e
            logging.error(f"Error: {e}")
            raise InternalServer(
                error_code=ErrorCode.SERVER_ERROR.name,
                errors={"message": ErrorCode.msg_server_error.value},
            )

    def _is_authorized(self, auth: JsonWebToken) -> bool:
        return auth.get("role") in [Role.ADMIN.name, Role.PATIENT.name]

    def _get_patient_id(
        self, auth: JsonWebToken, form_data: RequestCreateHealthCheckSchema
    ):
        return (
            auth.get("id")
            if auth.get("role") == Role.PATIENT.name
            else form_data.patient_id
        )

    async def _process_images(
        self, img_arr: List[Union[UploadFile, str]]
    ) -> List[ImageDailyHealthCheck]:
        images = []
        s3_service = S3Service()
        for img in img_arr:
            if isinstance(img, UploadFile):
                if not self._is_valid_image(img):
                    raise BadRequest(
                        error_code=ErrorCode.INVALID_FILE_TYPE.name,
                        errors={"message": "Invalid file type or size"},
                    )
                await img.seek(0)
                url = await s3_service.upload_file_from_form(img)
                if not url:
                    raise Forbidden(
                        error_code=ErrorCode.INVALID_FILE_TYPE.name,
                        errors={"message": "Failed to upload image to S3 bucket"},
                    )
                img_schema = ImageDailyHealthCheck(
                    image_url=url, image_name=img.filename, image_size=img.size
                )
                images.append(img_schema)
        return images

    def _is_valid_image(self, img: UploadFile) -> bool:
        valid_types = ["image/jpeg", "image/png", "image/jpg"]
        max_size = 1024 * 1024 * 5  # 5MB
        return img.content_type in valid_types and (img.size or 0) <= max_size
