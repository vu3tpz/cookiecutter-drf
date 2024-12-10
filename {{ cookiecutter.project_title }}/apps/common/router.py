from contextlib import suppress

from rest_framework.routers import SimpleRouter

from apps.common.helpers import random_n_token


class AppSimpleRouter(SimpleRouter):
    """Applications version of the `SimpleRouter`. Contains common and DRY stuff."""

    def get_default_basename(self, viewset):
        """Handle if the basename is not defined."""

        with suppress(AssertionError):
            return super().get_default_basename(viewset)

        # not defined, ignore
        return random_n_token()


router = AppSimpleRouter()
