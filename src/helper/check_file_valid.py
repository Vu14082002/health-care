
from starlette.datastructures import UploadFile
from src.config import config

from src.enum import ErrorCode
from src.core.exception import BadRequest
_data_img=["image/jpeg", "image/png","image/jpg","image/JPG","image/PNG","image/gif","image/GIF"]


def is_valid_image(file: UploadFile):
    if file.content_type not in _data_img:
        raise BadRequest(
            error_code=ErrorCode.BAD_REQUEST.name,
            errors={
                "message": "chỉ chấp nhận file ảnh có định dạng jpg, jpeg, png, gif"
            },
        )
    _expected_size_mb = config.IMG_SIZE_MB * 1024 * 1024
    _current_file_size = file.size if file.size else 0
    if _current_file_size > _expected_size_mb:
        raise BadRequest(
            error_code=ErrorCode.BAD_REQUEST.name,
            errors={
                "message": f"file ảnh không được vượt quá {_expected_size_mb}MB"
            },
        )
    return True


def is_valid_size_media(file: UploadFile):
    _expected_size_mb = config.MEDIA_SIZE_MB * 1024 * 1024
    _current_file_size = file.size if file.size else 0
    if _current_file_size > _expected_size_mb:
        raise BadRequest(
            error_code=ErrorCode.BAD_REQUEST.name,
            errors={
                "message": f"file media không được vượt quá {_expected_size_mb}MB"
            },
        )
    return True
