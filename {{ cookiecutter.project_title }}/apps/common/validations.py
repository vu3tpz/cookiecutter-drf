from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_pincode(value):
    if value > 999999 or value <= 100000:  # check if it has 6 digits or not
        raise ValidationError("Pincode must have only 6 digits.")


def validate_future_date(value):
    # Check if the date is in the past
    if value and value < timezone.now().date():
        raise ValidationError("Date must be in the future.")


def validate_past_date(value):
    # Check if the date is in the Future
    if value and value > timezone.now().date():
        raise ValidationError("Date must be in the past.")


def validate_future_today_date(value):
    # Check if the date is in the past and today
    if value and value <= timezone.now().date():
        raise ValidationError("Date must be in the future or today.")


def validate_past_today_date(value):
    # Check if the date is in the future and today
    if value and value >= timezone.now().date():
        raise ValidationError("Date must be in the past or today.")
