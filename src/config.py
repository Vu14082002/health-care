from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    class Config:
        env_file = ".env"

    ENV: str = "STAG"
    SENTRY_DSN: Optional[str] = None
    REDIS_URL: str
    REDIS_URL_WORKING_TIME: str
    BROKER_URL: str = Field(alias="broker_url")
    CELERY_ROUTES: dict = Field(
        default={
            "worker.on_admin_action": {"queue": "ait.admin_queue"}, },
        alias="task_routes",
    )
    CELERY_IMPORTS: list = Field(default=["src.tasks"], alias="imports")
    CELERY_RESULT_BACKEND: str = Field(
        default="rpc://", alias="result_backend")
    CELERY_TRACK_STARTED: bool = Field(
        default=True, alias="task_track_started")
    CELERY_RESULT_PERSISTENT: bool = Field(
        default=True, alias="result_persistent")

    POSTGRES_URL_MASTER: str
    POSTGRES_URL_SLAVE: str
    POSTGRES_URL_ELAMBIC: str
    PORT: str
    PREFIX_URL: Optional[str] = Field(default="/v1/admin")
    ACCESS_TOKEN: str
    REFRESH_TOKEN: str
    ALGORITHM: str
    SELF_URL: str = ''
    API_KEY: str = ''
    ACCOUNT_SID: str = ''
    AUTH_TOKEN: str = ''
    S3_BUCKET: str
    S3_KEY: str
    S3_SECRET: str
    REGION: str
    S3_ENDPOINT: str
    BOT_SERVICE_URL: str = ""


config = Config()
