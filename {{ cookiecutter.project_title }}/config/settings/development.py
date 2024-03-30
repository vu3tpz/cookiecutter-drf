from .base import *  # noqa & pylint: disable=wildcard-import

DEBUG = True

# Database Connection
# ------------------------------------------------------------------------------
{% if cookiecutter.local_database == 'SQLite' %}
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR / "db.sqlite3",
    }
}
{% else %}
DATABASES = {
    # default database user and credentials | others are added on runtime
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("LOCAL_DATABASE_DB", default=""),
        "USER": env.str("LOCAL_DATABASE_USER", default=""),
        "PASSWORD": env.str("LOCAL_DATABASE_PASSWORD", default=""),
        "HOST": env.str("LOCAL_DATABASE_HOST", default=""),
        "PORT": env.str("LOCAL_DATABASE_PORT", default=""),
    }
}
{% endif %}
