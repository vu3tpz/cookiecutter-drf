from apps.common.pagination import AppPagination
from apps.common.serializers import AppModelSerializer, simple_serialize_queryset
from apps.common.views.base import AppCreateAPIView, AppViewMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet


class AppGenericViewSet(GenericViewSet):
    """
    Applications version of the `GenericViewSet`. Overridden to implement
    app's necessary features. Also used in the CRUD viewsets.

    Note:
        1. An APIView is different from an APIViewSet.
        2. An APIView is registered using:
            path("url/endpoint/", APIView.as_view())
        3. An APIViewSet is registered using:
            router.register(
                "url/endpoint",
                APIViewSet,
                basename="base_name_if_needed",
            )

    Why is this implemented?
        > Consider an Update API that has to be implemented.
        > The API has to send the following:
            >> Initial data (ids).
            >> Metadata for select options.
            >> Handle the update operations.
        > If implemented using APIView, there has to be at least 2 view classes.
        > If implemented using APIViewSet, it is only one view.
        > Hence reduces the development time.
    """

    pass


class AppModelListAPIViewSet(
    AppViewMixin,
    ListModelMixin,
    AppGenericViewSet,
):
    """
    Applications base list APIViewSet. Handles all the listing views.
    This also sends the necessary filter meta and table config data.

    Also handles listing operations like sort, search, filter and
    table preferences of the user.

    References:
        1. https://github.com/miki725/django-url-filter
        2. https://www.django-rest-framework.org/api-guide/filtering/
    """

    pagination_class = AppPagination  # page-size: 25
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = []  # override
    search_fields = []  # override
    ordering_fields = "__all__"

    all_table_columns = {}

    @action(
        methods=["GET"],
        url_path="table-meta",
        detail=False,
    )
    def get_meta_for_table_handler(self, *args, **kwargs):
        """
        Sends out all the necessary config for the front-end table. The
        config can vary based on user permission and preference.
        """

        return self.send_response(data=self.get_meta_for_table())

    def get_meta_for_table(self) -> dict:
        """
        Just an adaptor class for the `get_meta_for_table_handler`.
        Overridden on the child classes to send data.
        """

        return {}

    def get_table_columns(self) -> dict:
        """
        Returns all the columns for the table in order. Got from the
        preference of the user. Overridden in child.
        """

        return self.all_table_columns

    def serialize_for_filter(self, queryset, fields=None):
        """Simple central function to serialize data for the filter component."""

        if not fields:
            fields = ["id", "identity"]

        return simple_serialize_queryset(queryset=queryset, fields=fields)

    def serialize_choices(self, choices: list):
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


class AppModelCUDAPIViewSet(
    AppViewMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    AppGenericViewSet,
):
    """
    What is CUD?
        Create, Update & Delete

    What is a CUD ViewSet?
        A ViewSet that handles the necessary CUD operations.

    Why is this separated from the ModelViewSet?
        User Permissions can be two types:
            > View
            > Modify
        An user can have anyone or both for a particular entity like `ProjectType`.
        These conditions can be handled easily, when the CUD is separated.

    Urls Allowed:
        > POST: {endpoint}/
            >> Get data from front-end and creates an object.
        > GET: {endpoint}/meta/
            >> Returns metadata for the front-end for object creation.

        > PUT: {endpoint}/<pk>/
            >> Get data from font-end to update an object.
        > GET: {endpoint}/<pk>/meta/
            >> Returns metadata for the front-end for object update.

        > DELETE: {endpoint}/<pk>/
            >> Deletes the object identified by the passed `pk`.
    """

    @action(
        methods=["GET"],
        url_path="meta",
        detail=False,
    )
    def get_meta_for_create(self, *args, **kwargs):
        """Returns the meta details for create from serializer."""

        return self.send_response(data=self.get_serializer().get_meta_for_create())

    @action(
        methods=["GET"],
        url_path="meta",
        detail=True,
    )
    def get_meta_for_update(self, *args, **kwargs):
        """Returns the meta details for update from serializer."""
        return self.send_response(
            data=self.get_serializer(instance=self.get_object()).get_meta_for_update()
        )


# Config for Meta fields to send for filters and other place where identity only used.
DEFAULT_IDENTITY_DISPLAY_FIELDS = (
    "id",
    "identity",
    "uuid",
)


class AbstractLookUpFieldMixin:
    """
    This class provides config for which field to look in the model as well as
    in url.
    """

    lookup_url_kwarg = "uuid"
    lookup_field = "uuid"


def get_upload_api_view(meta_model, meta_fields=None):
    """Central function to return the UploadAPIView. Used to handle uploads."""

    if not meta_fields:
        meta_fields = ["file", "id"]

    class _View(AppCreateAPIView):
        """View to handle the upload."""

        class _Serializer(AppModelSerializer):
            """Serializer for write."""

            class Meta(AppModelSerializer.Meta):
                model = meta_model
                fields = meta_fields

        parser_classes = [parsers.MultiPartParser]
        serializer_class = _Serializer

        def create(self, request, *args, **kwargs):
            file_size_limit = 5 * 1024 * 1024  # 5 MB in bytes

            if "file" not in request.data:
                return self.send_error_response(data={"detail": "File not found in the request"})

            uploaded_file = request.data["file"]
            if uploaded_file.size > file_size_limit:
                return self.send_error_response(
                    data={"detail": "File size exceeds the limit of 5 MB"}
                )

            return super().create(request, *args, **kwargs)

    return _View
