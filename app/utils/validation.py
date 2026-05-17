from typing import Any, Type
from pydantic import BaseModel, ValidationError as PydanticError, ConfigDict
from app.middleware.error_handler import ValidationError


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


def parse_body(model: Type[BaseSchema], payload: Any) -> BaseSchema:
    """
    Parse request body and validate using Pydantic model.
    Raises ValidationError on invalid data.
    """
    try:
        return model.model_validate(payload)
    except PydanticError as exc:
        raise ValidationError('Validation failed', details=_format_errors(exc))


def parse_query(model: Type[BaseSchema], payload: Any) -> BaseSchema:
    """
    Parse query parameters and validate using Pydantic model.
    Raises ValidationError on invalid data.
    """
    try:
        return model.model_validate(payload)
    except PydanticError as exc:
        raise ValidationError('Validation failed', details=_format_errors(exc))


def _format_errors(exc: PydanticError) -> list[dict]:
    """
    Format Pydantic validation errors into a list of field error objects.
    """
    details = []
    for err in exc.errors():
        loc = '.'.join(str(p) for p in err.get('loc', [])) or 'unknown'
        msg = err.get('msg', 'Invalid value')
        details.append({'field': loc, 'message': msg})
    return details
