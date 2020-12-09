from datetime import datetime
import pytz
from src.settings import TIME_ZONE as _django_settings_time_zone


def get_tz_aware_dt_from_timestamp(timestamp: float) -> datetime:
    """
    Convert a UNIX-like timestamp into a timezone aware datetime object
    for the current django timezone.

    Args:
        timestamp (float): The UNIX timestamp

    Returns:
        datetime: A django-native TZ-aware datetime object
    """
    tz = pytz.timezone(zone=_django_settings_time_zone)
    # this method is superior to `make_aware` to avoid conflicts with system specifications.
    # read: https://stackoverflow.com/questions/12589764/unix-timestamp-to-datetime-in-django-with-timezone/32163867#32163867
    return datetime.fromtimestamp(timestamp, tz)
