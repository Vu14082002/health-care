# -*- coding: utf-8 -*-
import logging
import mimetypes
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import boto3
import boto3.session
from botocore.exceptions import ClientError
from starlette.datastructures import UploadFile

from src.config import config


class S3Service(object):
    def __init__(self) -> None:
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=config.S3_KEY,
            aws_secret_access_key=config.S3_SECRET,
            endpoint_url=config.S3_ENDPOINT,
            region_name=config.REGION,
            config=boto3.session.Config(
                signature_version="s3v4", s3={"addressing_style": "path"}
            ),
        )

    async def upload_file_from_form(
        self, file: UploadFile, bucket_name=config.S3_BUCKET
    ):
        month = "{:02d}".format(datetime.now(timezone.utc).month)
        day = "{:02d}".format(datetime.now(timezone.utc).day)
        year = datetime.now(timezone.utc).year
        key = f"user_upload/{year}/{month}/{day}/{str(uuid4())}{file.filename}"
        # Guess the MIME type
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"
        await file.seek(0)
        content = await file.read()
        buffer = BytesIO()
        _ = buffer.write(content)
        _ = buffer.seek(0)
        try:
            self.s3.upload_fileobj(
                buffer,
                Bucket=bucket_name,
                Key=key,
                ExtraArgs={"ACL": "public-read", "ContentType": content_type},
            )
        except ClientError as e:
            logging.error(f"Error uploading file to s3: {e}")
            raise e

        link = f"{config.S3_ENDPOINT}/{bucket_name}/{key}"
        return link

    # upload_file_from_form data type is bytes
    async def upload_file_from_bytes(
        self, file: bytes, filename: str, bucket_name=config.S3_BUCKET
    ):
        month = "{:02d}".format(datetime.now(timezone.utc).month)
        day = "{:02d}".format(datetime.now(timezone.utc).day)
        year = datetime.now(timezone.utc).year
        key = f"user_upload/{year}/{month}/{day}/{str(uuid4())}{filename}"

        content_type = "application/octet-stream"

        buffer = BytesIO(file)
        buffer.seek(0)
        try:
            self.s3.upload_fileobj(
                buffer,
                Bucket=bucket_name,
                Key=key,
                ExtraArgs={"ACL": "public-read", "ContentType": content_type},
            )
        except ClientError as e:
            logging.error(f"Error uploading file: {e}")
            return None
        link = f"{config.S3_ENDPOINT}/{bucket_name}/{key}"
        return link
