

import json
from datetime import date, datetime


def json_serializable(obj):
    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable")

    return json.loads(json.dumps(obj, default=default))
