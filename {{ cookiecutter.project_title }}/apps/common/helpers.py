import calendar
import datetime
import json
import random
import secrets
import string
import time
import typing

import inflect
from dateutil import tz
from django.conf import settings
from requests import request


def create_log(data: typing.Any, category: str):
    """
    A centralized function to create the app logs. Just in case some
    extra pre-processing are to be added in the future.
    """

    # assert data and category, "The passed parameters cannot be None while creating log."
    # apps.get_model("common.Log").objects.create(data=data, category=category)

    if settings.DEBUG:
        print("Log: ", data, category)  # noqa


def get_display_name_for_slug(slug: str):
    """
    For a given string slug this generates the display name for the given slug.
    This generated display name will be displayed on the front end.
    """

    try:
        return slug.replace("_", " ").title()
    except:  # noqa
        return slug


def flatten(value):
    return [item for sublist in value for item in sublist]


def random_n_digits(n):
    """Returns a random number with `n` length."""

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return str(random.randint(range_start, range_end))


def random_n_token(n=10):
    """Generate a random string with numbers and characters with `n` length."""

    allowed_characters = string.ascii_letters + string.digits  # contains char and digits
    return "".join(secrets.choice(allowed_characters) for _ in range(n))


def make_http_request(
    url: str, method="GET", headers={}, data={}, params={}, auth=None, **kwargs  # noqa
):
    """
    Function that makes a third party http request to any given url based on the passed params.
    This is similar to triggerSimpleAjax/Axios function. This is defined here just to make things DRY.
    """

    response = request(
        method=method,
        url=url,
        headers=headers,
        data=stringify(data),
        params=params,
        auth=auth,
        **kwargs,
    )

    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        response_data = None

    _output = {
        "data": response_data,
        "status_code": response.status_code,
        "reason": None if response_data else response.text,  # fallback for the data
    }

    # logging action
    log = {
        "request_data": data,
        "params": params,
        "headers": headers,
        "method": method,
        "response_data": _output,
    }
    # log_outbound_message(stringify(log), url, "make_http_request")

    if settings.DEBUG:
        print(log)  # noqa

    return _output


def stringify(data, fallback=None):  # noqa
    """Stringify a given data."""

    try:
        return json.dumps(data)
    except:  # noqa
        return fallback


def convert_utc_to_local_timezone(
    input_datetime: datetime.date | datetime.datetime,
    inbound_request,  # noqa
):
    """
    Given a UTC datetime or date object, this will convert it to the
    user's local timezone based on the request.
    """

    from_zone = tz.gettz(settings.TIME_ZONE)

    # TODO: from `inbound_request`
    to_zone = tz.gettz("Asia/Kolkata")

    input_datetime = input_datetime.replace(tzinfo=from_zone)

    return input_datetime.astimezone(to_zone)


def is_any_or_list1_in_list2(list1: list, list2: list):
    """Given two lists, this will check if any element of list1 is in list2."""

    return any(v in list2 for v in list1)


def get_first_of(*args):
    """For _ in args, returns the first value whose value is valid."""

    for _ in args:
        if _:
            return _

    return None


def get_file_field_url(instance, field="image"):
    """Given any instance and a linked File or Image field, returns the url."""

    if getattr(instance, field, None):
        return getattr(instance, field).file.url

    return None


def pause_thread(seconds):
    """Pause the tread for the given seconds."""

    time.sleep(seconds)


def get_first_last_dates(month, year):
    """
    get the first and last date of the month
    """
    first_date = datetime.datetime(year, month, 1)
    last_day = (first_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(
        days=1
    )

    return first_date, last_day


def get_number_of_days_in_month(month, year):
    """
    get number of days in month
    """
    month = month
    year = year
    return calendar.monthrange(year, month)[1]


def get_month_in_word(month):
    """
    return month in word format
    """
    return calendar.month_name[int(month)]


def number_to_words(number):
    p = inflect.engine()
    return p.number_to_words(number)
