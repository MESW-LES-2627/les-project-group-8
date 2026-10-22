"""Small input checks reused by every module's service."""

from .errors import ValidationError


def require_json_object(payload) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    return payload


def required_text(payload: dict, field: str, max_length: int) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Field '{field}' cannot be empty.")
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(f"Field '{field}' must be at most {max_length} characters.")
    return value
