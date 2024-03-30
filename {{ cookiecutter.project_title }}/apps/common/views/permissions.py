from apps.common.helpers import is_any_or_list1_in_list2
from django.core import exceptions


class HasValidPermissionMixin:
    """
    Checks if the user has the below told permission to access the view.
    if not, raises the permission error to the user.
    """

    required_permission: str | list[str] = None

    def check_permissions(self, request):
        """Perform the check."""

        # pre-process
        if type(self.required_permission) == str:
            self.required_permission = [self.required_permission]

        super().check_permissions(request=request)

        if (
            request.user
            and request.user.is_authenticated
            and self.required_permission
            and not is_any_or_list1_in_list2(
                list1=self.required_permission,
                list2=self.get_organisation_user().permissions,
            )
        ):
            raise exceptions.PermissionDenied()
