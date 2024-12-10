import json
import random
import secrets
import string


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


def stringify(data, fallback=None):  # noqa
    """Stringify a given data."""

    try:
        return json.dumps(data)
    except:  # noqa
        return fallback


def get_file_field_url(instance, field="image"):
    """Given any instance and a linked File or Image field, returns the url."""

    if getattr(instance, field, None):
        return getattr(instance, field).file.url

    return None
