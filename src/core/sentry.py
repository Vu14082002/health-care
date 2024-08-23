from src.core import logger

import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.exceptions import HTTPException


def setup(dsn):
    """
     Setup Sentry to receive data. This is called from : func : ` ~flask. Flask. setup `
     
     @param dsn - The dsn to use
    """
    # Initialize the sentry SDK. If dsn is not set the dsn is used.
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
        )
        logger.debug("Config sentry successfully")

    else:
        logger.debug("Sentry not config")
