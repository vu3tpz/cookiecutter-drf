from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The email is must for user."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

    def get_or_none(self, *args, **kwargs):
        """
        Get the object based on the given **kwargs. If not present returns None.
        Note: Expects a single instance.
        """

        try:
            return self.get(*args, **kwargs)
        # if does not exist or if idiotic values like id=None is passed
        except (
            ObjectDoesNotExist,
            AttributeError,
            ValueError,
            MultipleObjectsReturned,
            ValidationError,  # invalid UUID
        ):
            return None


class BaseObjectManagerQuerySet(QuerySet):
    """
    The main/base manager for the apps models. This is used for including common
    model filters and methods. This is used just to make things DRY.

    This can be used in both ways:
        1. Model.app_objects.custom_method()
        2. Model.app_objects.filter().custom_method()

    Reference:
    https://stackoverflow.com/questions/2163151/custom-queryset-and-manager-without-breaking-dry#answer-21757519

    Usage on the model class
        objects = BaseObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        active,
        inactive,
        alive,
        dead,
        delete,
        hard_delete
    """

    def get_or_none(self, *args, **kwargs):
        """
        Get the object based on the given **kwargs. If not present returns None.
        Note: Expects a single instance.
        """

        try:
            return self.get(*args, **kwargs)
        # if does not exist or if idiotic values like id=None is passed
        except (
            ObjectDoesNotExist,
            AttributeError,
            ValueError,
            MultipleObjectsReturned,
            ValidationError,  # invalid UUID
        ):
            return None

    def delete(self):
        """
        Soft-delete the queryset by updating `is_deleted` and `is_active`
        fields to True and False respectively.
        """

        return super().update(is_deleted=True, is_active=False, deleted_at=timezone.now())

    def hard_delete(self):
        """
        Hard-delete the queryset by calling the default `delete` method
        of the queryset.
        """

        return super().delete()

    def alive(self):
        """
        Return a queryset of only the non-soft-deleted objects, which have
        `is_deleted` set to False.
        """

        return self.filter(is_deleted=False)

    def dead(self):
        """
        Return a queryset of only the soft-deleted objects, which have
        `is_deleted` set to True.
        """

        return self.filter(is_deleted=True)

    def active(self):
        """
        Overridden to set archivable fields. Return a queryset of only the active objects, which have `is_active`
        set to True and `is_deleted` set to False.
        """

        return self.filter(is_active=True, is_deleted=False)

    def inactive(self):
        """
        Overridden to set archivable fields. Return a queryset of only the inactive objects, which have `is_active`
        set to False and `is_deleted` set to False.
        """

        return self.filter(is_active=False, is_deleted=False)
