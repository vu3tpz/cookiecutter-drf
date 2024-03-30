import uuid

from apps.common.helpers import get_display_name_for_slug
from apps.common.models import COMMON_CHAR_FIELD_MAX_LENGTH
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class BaseField:
    """Base field for the application defined model fields."""

    pass


class AppSingleChoiceField(BaseField, models.CharField):
    """
    Field to input a single choice input from the user. A select input.

    Basically a CharField with choices. This is used as a replacement for
    model_util.StatusField since that makes us write a lot of duplicate code.

    For the schema of `choices_config`, see `BASE_MODEL_STATUS_CONFIG`. This contains
    some model field kwargs, and the options are basically slugs.

    This gets the display name of the slugs by pre processing them. And also sets
    the max_length dynamically.
    """

    def __init__(self, choices_config: dict, *args, **kwargs):
        self.choices_config = choices_config
        self.options = self.choices_config["options"]

        generated_choices, max_length = [], 0
        for option in self.options:
            # option setting & max length setting
            if self.type_of_options() in ["list_of_tuples"]:
                generated_choices.append(option)
                if len(option[0]) > max_length:
                    max_length = len(option[0])

            else:
                generated_choices.append((option, self.get_display_name(option)))
                if len(option) > max_length:
                    max_length = len(option)

        kwargs.update(
            {
                "choices": generated_choices,
                "max_length": max_length,
            }
        )
        super().__init__(*args, **kwargs)

    def get_display_name(self, option):
        """Returns the display name for the given option."""

        return (
            self.options[option]
            if self.type_of_options() in ["dict"]
            else get_display_name_for_slug(option)
        )

    def type_of_options(self):
        """
        Returns the type of options passed as input. It can either be a
        dict or a list. Just a DRY function to determine and make decisions.
        """

        _type = type(self.options).__name__

        if _type == "list":
            _option_to_consider = self.options[0]
            if (
                type(_option_to_consider) not in [str]
                and type(_option_to_consider).__name__ == "tuple"
            ):
                _type = "list_of_tuples"

        return _type

    def deconstruct(self):
        """
        Overridden because of custom params.
        Reference: https://docs.djangoproject.com/en/3.1/howto/custom-model-fields/
        """

        name, path, args, kwargs = super().deconstruct()
        kwargs["choices_config"] = self.choices_config
        return name, path, args, kwargs

    def get_default_option(self) -> None | str:
        """Returns the default option based on the defined configuration."""

        if self.type_of_options() in ["list"]:
            return self.choices_config.get("default", self.options[0])

        if self.type_of_options() in ["list_of_tuples"]:
            return self.choices_config.get("default", self.options[0][0])

        # get default from dict keys
        return self.choices_config.get("default", [*self.options.keys()][0])

    def is_nullable(self) -> bool:
        """Returns a bool, that if this field can allow null values or not."""

        return None in [*self.options, self.get_default_option()]


class AppPhoneNumberField(BaseField, PhoneNumberField):
    """Applications version of the PhoneNumberField. To define app's functions."""

    pass


class AppSingleFileField(BaseField, models.FileField):
    """Field for uploading a single file. Sets the default upload path."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("upload_to", "files/")
        kwargs.setdefault("max_length", COMMON_CHAR_FIELD_MAX_LENGTH)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        # Generate a new filename with UUID and keep the existing path
        if model_instance.file:
            _, extension = model_instance.file.name.split(".")
            new_filename = f"{uuid.uuid4().hex}.{extension}"

            # Set the new filename without changing the path
            model_instance.file.name = f"{new_filename}"

        return super().pre_save(model_instance, add)
