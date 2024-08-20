from src.core.logger import logger

import sentry_sdk

def setup(dsn):
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[],
            traces_sample_rate=1.0,
            send_default_pii=True,
        )
        logger.debug("Config sentry successfully")

    else:
        logger.debug("Sentry not config")

