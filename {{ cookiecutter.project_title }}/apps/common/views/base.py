from contextlib import suppress

from apps.common.config import API_RESPONSE_ACTION_CODES
from rest_framework import permissions, status
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import is_success
from rest_framework.views import APIView


class NonAuthenticatedAPIMixin:
    """
    The mixin class which defines an API class as non-authenticated.
    The users can access this api without login. Just DRY stuff.
    """

    permission_classes = [permissions.AllowAny]


class AppViewMixin:
    """
    The base view class for all the application view. Contains common methods
    and overrides to main integrity and schema.
    """

    def get_request(self):
        """Returns the request."""

        return self.request

    def get_user(self):
        """Returns the current user."""

        return self.get_request().user

    def get_authenticated_user(self):
        """Returns the authenticated user."""

        user = self.get_user()
        return user if user and user.is_authenticated else None

    def send_error_response(self, data=None):
        """Central function to send error response."""

        return self.send_response(data=data, status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_response(
        data=None, status_code=status.HTTP_200_OK, action_code="DO_NOTHING", **other_response_data
    ):
        """Custom function to send the centralized response."""

        return Response(
            data={
                "data": data,
                "status": "success" if is_success(status_code) else "error",
                "action_code": action_code,  # make the FE do things based on this
                **other_response_data,
            },
            status=status_code,
        )

    def get_app_response_schema(self, response: Response, **kwargs):
        """Given a drf response object. This converts it to the application schema."""

        return self.send_response(data=response.data, status_code=response.status_code, **kwargs)

    def handle_exception(self, exc):
        """Overridden to maintain applications response schema."""

        # pre-process action code
        action_code = API_RESPONSE_ACTION_CODES["display_error_1"]
        if exc and hasattr(exc, "status_code") and exc.status_code in [401]:
            action_code = "AUTH_TOKEN_NOT_PROVIDED_OR_INVALID"

        return self.get_app_response_schema(super().handle_exception(exc), action_code=action_code)

    def list(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().list(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def retrieve(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().retrieve(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def create(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().create(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def update(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().update(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def destroy(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().destroy(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)

    def partial_update(self, request, *args, **kwargs):
        """Overridden to maintain applications response schema."""

        with suppress(AttributeError):
            return self.get_app_response_schema(super().partial_update(request, *args, **kwargs))

        # not defined in view, not allowed
        raise MethodNotAllowed(method=self.get_request().method)


class AppAPIView(AppViewMixin, APIView):
    """
    Common api view class for the entire application. Just a central view to customize
    the output response schema. The entire application will follow this schema.
    """

    sync_action_class = None
    get_object_model = None
    serializer_class = None

    def get_valid_serializer(self, instance=None):
        """Central function to get the valid serializer. Raises exceptions."""

        assert self.serializer_class

        # pylint: disable=not-callable
        serializer = self.serializer_class(
            data=self.request.data,
            context=self.get_serializer_context(),
            instance=instance,
        )
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_serializer_context(self):
        """Central function to pass the serializer context."""

        return {"request": self.get_request()}

    def adopt_sync_action_class(self, instance):
        """
        Given the instance of `BaseSyncAction`, this function will adopt the action
        and will send the necessary responses accordingly. DRY function.
        """

        assert self.sync_action_class

        # pylint: disable=not-callable
        success, result = self.sync_action_class(
            instance=instance, request=self.get_request()
        ).execute()

        if success:
            return self.send_response(data=result)

        return self.send_error_response(data=result)

    def get_object(self, exception=NotFound, identifier="pk"):
        """
        Suppose you want to list data based on an other model. This
        is a centralized function to do the same.
        """
        if self.get_object_model:
            _object = self.get_object_model.objects.get_or_none(
                **{identifier: self.kwargs[identifier]}
            )

            if not _object:
                raise exception

            return _object

        return super().get_object()

    def choices_for_meta(self, choices: list):
        """
        Given a list of choices like:
            ['active', ...]

        This will return the following:
            [{'id': 'active', 'identity': 'Active'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]


class AppCreateAPIView(AppViewMixin, CreateAPIView):
    """App's version on the `CreateAPIView`, implements custom handlers."""

    def perform_create(self, serializer):
        """Overridden to call the post create handler."""

        instance = serializer.save()
        self.perform_post_create(instance=instance)

    def perform_post_create(self, instance):
        """Called after `perform_create`. Handle custom logic here."""

        pass
