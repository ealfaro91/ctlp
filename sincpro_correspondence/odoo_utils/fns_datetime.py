from datetime import date, datetime
from typing import Tuple

import pytz


def from_naive_utc_to_bo_datetime(utc_datetime: datetime) -> datetime:
    """
    Convert a naive UTC datetime to a Bolivia datetime
    """
    aware_utc_datetime = utc_datetime.replace(tzinfo=pytz.utc)
    bo = pytz.timezone("America/La_Paz")
    bo_datetime = aware_utc_datetime.astimezone(bo)
    return bo_datetime


def from_naive_utc_to_bolivia_string(bo_datetime: datetime) -> str:
    """
    Convert a naive UTC datetime to a Bolivia string
    """
    bo_datetime = from_naive_utc_to_bo_datetime(bo_datetime)
    return bo_datetime.strftime("%Y-%m-%d %H:%M:%S")


def transform_datetime_to_bolivia_tz(
    date_from: datetime, date_to: datetime
) -> Tuple[datetime, datetime]:
    date_from = date_from.replace(tzinfo=pytz.utc)
    date_to = date_to.replace(tzinfo=pytz.utc)

    date_from = date_from.astimezone(pytz.timezone("America/La_Paz"))
    date_to = date_to.astimezone(pytz.timezone("America/La_Paz"))
    return date_from, date_to


def today_bolivia() -> date:
    today = datetime.now()
    bo = pytz.timezone("America/La_Paz")
    today = today.astimezone(bo)
    return today.date()
