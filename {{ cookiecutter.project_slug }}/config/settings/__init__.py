# flake8: noqa & pylint: disable=no-member
import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# environment based settings module import
if ENVIRONMENT == "development":
    from .development import *
elif ENVIRONMENT == "deployment":
    from .deployment import *
else:
    raise NotImplementedError(
        f"Environment related settings not found! Please make sure "
        f"settings/{ENVIRONMENT}.py is present."
    )
