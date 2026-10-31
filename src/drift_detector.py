"""Schema drift reporting."""
from .schema_validator import validate_schema


def detect_drift(frame):
    result = validate_schema(frame)
    return {"has_drift": bool(result["drift"] or result["issues"]), **result}
