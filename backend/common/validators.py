import re
from django.core.exceptions import ValidationError

PHONE_RE = re.compile(r"^\+998\d{9}$")


def validate_uz_phone(value: str) -> None:
    if not PHONE_RE.match(value):
        raise ValidationError("Telefon raqami +998XXXXXXXXX formatida bo'lishi kerak.")


def validate_positive_amount(value) -> None:
    if value is None or value <= 0:
        raise ValidationError("Summa musbat bo'lishi kerak.")