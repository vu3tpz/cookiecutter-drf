from .base import *  # noqa & pylint: disable=wildcard-import

DEBUG = True

# Database Connection
# ------------------------------------------------------------------------------
"{% if cookiecutter.local_database == 'PostgreSQL' %}"
DATABASES = {
    # default database user and credentials | others are added on runtime
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DATABASE_DB", default=""),
        "USER": env.str("DATABASE_USER", default=""),
        "PASSWORD": env.str("DATABASE_PASSWORD", default=""),
        "HOST": env.str("DATABASE_HOST", default=""),
        "PORT": env.str("DATABASE_PORT", default=""),
    }
}
"{% else %}"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR / "db.sqlite3",
    }
}
"{% endif %}"
