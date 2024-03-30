from apps.common.managers import UserManager
from apps.common.model_fields import AppPhoneNumberField, AppSingleChoiceField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)
from django.contrib.auth.models import AbstractUser
from django.db import models

from .config import USER_TITLE_CHOICES


class User(BaseModel, AbstractUser):
    """
    User model for the entire application.
    This models holds data other than auth related data.
    Holds information of user.
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    username = None
    email = models.EmailField(unique=True)
    phone_number = AppPhoneNumberField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    password = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    title = AppSingleChoiceField(
        choices_config=USER_TITLE_CHOICES, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    first_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    last_name = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
