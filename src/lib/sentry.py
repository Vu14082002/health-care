from src.lib.logger import logger

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.exceptions import HTTPException

def custom_filter(event, hint):
    # Check if the error originated from a socket operation
    if "socket" in event.get("extra", {}):
        return None
    return event

def setup(dsn):
    if dsn:
        logger.debug(dsn)
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
            ],
            traces_sample_rate=1.0,
            send_default_pii=True,
            enable_tracing=True,
            send_client_reports=False,
            before_send=custom_filter,
        )
        logger.debug("Config sentry successfully")

    else:
        logger.debug("Sentry not config")
