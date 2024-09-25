from datetime import datetime, timedelta, timezone, date


class TimeHelper:

    def __init__(self) -> None:
        pass

    def get_cur_time_epoch_second(self):
        """this function returns the current time in epoch seconds format
        from the current time in UTC 0 timezone
        Returns:
            int: seconds since epoch
        """
        utc_plus_7 = timezone(timedelta(hours=7))
        int(datetime.now(utc_plus_7).timestamp())
        return int(datetime.now(timezone.utc).timestamp())

    def get_current_date_time(self):
        """This function returns the current date in UTC+7 timezone with the time set to 00:00:00.

        Returns:
            datetime: Current date at 00:00:00 in UTC+7 timezone.
        """
        utc_plus_7 = timezone(timedelta(hours=7))
        current_date = datetime.now(utc_plus_7).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return current_date

    def get_current_date(self):
        return date.today()
