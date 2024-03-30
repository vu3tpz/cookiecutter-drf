import uuid
from contextlib import suppress

from apps.common.managers import BaseObjectManagerQuerySet
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models

# top level config
COMMON_CHAR_FIELD_MAX_LENGTH = 512
COMMON_NULLABLE_FIELD_CONFIG = {  # user for API based stuff
    "default": None,
    "null": True,
}
COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {  # user for Form/app based stuff
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}


class BaseModel(models.Model):
    """
    Contains the last modified and the created fields, basically
    the base model for the entire app.
    """

    # unique id field
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    # time tracking
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # by whom
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="created_%(class)s",
        on_delete=models.SET_DEFAULT,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    # custom manager
    objects = BaseObjectManagerQuerySet.as_manager()

    class Meta:
        abstract = True

    @classmethod
    def get_model_fields(cls):
        """
        Returns all the model fields. This does not
        include the defined M2M & related fields.
        """

        return cls._meta.fields

    @classmethod
    def get_all_model_fields(cls):
        """
        Returns all model fields, this includes M2M and related fields.
        Note: The field classes will be different & additional here.
        """

        return cls._meta.get_fields()

    @classmethod
    def get_model_field_names(cls, exclude=[]):  # noqa
        """Returns only the flat field names of the model."""

        exclude = ["id", "created_by", "created", "modified", *exclude]
        return [_.name for _ in cls.get_model_fields() if _.name not in exclude]

    @classmethod
    def get_model_field(cls, field_name, fallback=None):
        """Returns a single model field given by `field_name`."""

        with suppress(FieldDoesNotExist):
            return cls._meta.get_field(field_name)

        return fallback


class FileOnlyModel(BaseModel):
    """
    Parent class for all the file only models. This is used as a common class
    and for differentiating field on the run time.

    This will contain only:
        file = model_fields.AppSingleFileField(...)

    This model is then linked as a foreign key where ever necessary.
    """

    class Meta(BaseModel.Meta):
        abstract = True


class BaseIdentityModel(BaseModel):
    """
    The model class that includes identity. Identity is basically a `name`.
    This is applicable for anything like City etc.
    """

    class Meta(BaseModel.Meta):
        abstract = True

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, verbose_name="Name/Title")

    description = models.TextField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def __str__(self):
        return self.identity
