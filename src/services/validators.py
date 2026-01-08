import re
from datetime import datetime
from .exceptions import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9 +()-]{6,30}$")

def require_nonempty(value: str, field: str) -> str:
    if value is None or str(value).strip() == "":
        raise ValidationError(f"Pole '{field}' nesmí být prázdné.")
    return str(value).strip()

def validate_email(email: str) -> str:
    email = require_nonempty(email, "email")
    if not EMAIL_RE.match(email):
        raise ValidationError("Neplatný e-mail.")
    return email

def validate_phone(phone: str) -> str:
    phone = require_nonempty(phone, "telefon")
    if not PHONE_RE.match(phone):
        raise ValidationError("Neplatný formát telefonu.")
    return phone

def validate_positive_int(value: str, field: str) -> int:
    try:
        i = int(value)
    except ValueError:
        raise ValidationError(f"Pole '{field}' musí být celé číslo.")
    if i <= 0:
        raise ValidationError(f"Pole '{field}' musí být > 0.")
    return i

def validate_float(value: str, field: str) -> float:
    try:
        f = float(value)
    except ValueError:
        raise ValidationError(f"Pole '{field}' musí být číslo.")
    return f

def parse_datetime(value: str) -> datetime:
    value = require_nonempty(value, "datum a čas")
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValidationError("Špatný formát datumu/času. Použij: YYYY-MM-DD HH:MM")
