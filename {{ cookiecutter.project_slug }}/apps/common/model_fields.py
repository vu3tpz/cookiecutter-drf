import uuid

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.helpers import get_display_name_for_slug


class BaseField:
    """Base field for the application defined model fields."""

    pass


class AppPhoneNumberField(BaseField, PhoneNumberField):
    """Applications version of the PhoneNumberField. To define app's functions."""

    pass


class AppSingleFileField(BaseField, models.FileField):
    """Field for uploading a single file. Sets the default upload path."""

    def __init__(self, *args, **kwargs):
        from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH

        kwargs.setdefault("upload_to", "files/")
        kwargs.setdefault("max_length", COMMON_CHAR_FIELD_MAX_LENGTH)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        # Generate a new filename with UUID and keep the existing path
        if model_instance.file:
            extension = model_instance.file.name.split(".")[-1]
            new_filename = f"{uuid.uuid4().hex}.{extension}"

            # Set the new filename without changing the path
            model_instance.file.name = f"{new_filename}"

        return super().pre_save(model_instance, add)
