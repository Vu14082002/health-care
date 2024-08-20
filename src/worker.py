import asyncio
import json

from celery import Celery

from src.config import config
from src.core.logger import logger


class AsyncCelery(Celery):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance") or not cls.instance:
            cls.instance = super().__new__(cls)
        logger.debug("Broker url: {}".format(config.BROKER_URL))
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patch_task()

    def patch_task(self):
        TaskBase = self.Task

        class ContextTask(TaskBase):
            abstract = True
            loop = asyncio.new_event_loop()

            def _run(self, *args, **kwargs):
                result = self.loop.run_until_complete(
                    TaskBase.__call__(self, *args, **kwargs)
                )
                return result

            def __call__(self, *args, **kwargs):
                return self._run(*args, **kwargs)

        self.Task = ContextTask


def create_worker():
    _celery = AsyncCelery(
        __name__, broker=config.BROKER_URL, backend=config.CELERY_RESULT_BACKEND
    )
    _conf_json: dict = json.loads(config.model_dump_json(by_alias=True))
    _celery.conf.update(_conf_json)
    return _celery


worker = create_worker()
