from .base import *  # noqa & pylint: disable=wildcard-import

DEBUG = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR / "db.sqlite3",
    }
}
