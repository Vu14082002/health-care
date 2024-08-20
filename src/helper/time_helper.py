
from datetime import datetime, timezone


class TimeHelper:

    def __init__(self) -> None:
        pass

    def get_cur_time_epoch_second(self) -> int:
        """this function returns the current time in epoch seconds format
        from the current time in UTC 0 timezone
        Returns:
            int: seconds since epoch
        """
        return int(datetime.now(timezone.utc).timestamp())
