import inspect
from collections.abc import Callable

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from mirascope.core.base.from_call_args import FromCallArgs


def get_call_args_field_names_and_validate(
    response_model: object, fn: Callable
) -> set[str]:
    if not (inspect.isclass(response_model) and issubclass(response_model, BaseModel)):
        return set()
    call_args_fields = _get_call_args_field_names(response_model)
    _validate_call_args(fn, call_args_fields)
    return call_args_fields


def is_from_call_args(field: FieldInfo) -> bool:
    return any(isinstance(m, FromCallArgs) for m in field.metadata)


def _get_call_args_field_names(response_model: type[BaseModel]) -> set[str]:
    """
    This function is used to get the field names that are marked with the `FromCallArgs` metadata.
    The function doesn't treat the nested fields such like lists or dictionaries.
    """

    exclude_fields: set[str] = set()
    for field_name, field in response_model.model_fields.items():
        if is_from_call_args(field):
            exclude_fields.add(field_name)
    return exclude_fields


def _validate_call_args(fn: Callable, call_args_fields: set[str]) -> None:
    if not call_args_fields:
        return None
    signature = inspect.signature(fn)
    arguments = signature.parameters.keys()
    if call_args_fields.issubset(arguments):
        return None
    raise ValueError(
        f"The function arguments do not contain all the fields marked with `FromCallArgs`. {arguments=}, {call_args_fields=}"
    )
