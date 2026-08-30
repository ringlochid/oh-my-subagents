from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from oh_my_subagents.interfaces.http.contracts.operation_failure import (
    OperationFailure,
    ProductFailureCode,
)
from oh_my_subagents.operator.tools.contracts import OperatorTool, OperatorToolResult
from oh_my_subagents.workflows.errors import WorkflowInputError, WorkflowValidationIssue

_UNCERTAIN_OPERATION_RESULT: OperatorToolResult = {
    "error": "operator_operation_outcome_uncertain",
    "message": (
        "The Oh My Subagents operation did not return an accepted result. "
        "Do not repeat it automatically; refetch current product truth."
    ),
}


@dataclass(frozen=True, slots=True)
class OperatorToolInvocationResult:
    payload: OperatorToolResult
    is_error: bool


async def invoke_operator_tool(
    tool: OperatorTool,
    arguments: object,
) -> OperatorToolInvocationResult:
    """Call one typed Operator leaf and preserve rejection versus uncertainty."""

    try:
        request = tool.input_model.model_validate(arguments)
    except ValidationError as exc:
        return OperatorToolInvocationResult(
            payload=_validation_failure(exc).model_dump(mode="json", by_alias=True),
            is_error=True,
        )
    try:
        payload = await tool.call_validated(request)
    except Exception:
        return uncertain_operator_tool_result()
    return OperatorToolInvocationResult(payload=payload, is_error=False)


def reject_operator_tool_request(
    *,
    field_path: str,
) -> OperatorToolInvocationResult:
    """Reject one malformed provider tool envelope before selecting a leaf."""

    return OperatorToolInvocationResult(
        payload=_invalid_request_failure(field_path=field_path).model_dump(
            mode="json",
            by_alias=True,
        ),
        is_error=True,
    )


def uncertain_operator_tool_result() -> OperatorToolInvocationResult:
    """Return the redacted result for a call whose accepted outcome is unknown."""

    return OperatorToolInvocationResult(
        payload=dict(_UNCERTAIN_OPERATION_RESULT),
        is_error=True,
    )


def _validation_failure(exc: ValidationError) -> OperationFailure:
    first_error = exc.errors(include_input=False, include_url=False)[0]
    workflow_issue = _workflow_input_issue(first_error)
    if workflow_issue is not None:
        return OperationFailure.model_validate(
            {
                "code": ProductFailureCode.INVALID_REQUEST,
                "summary": "The Workflow contains an unsupported or invalid field.",
                "retryable": False,
                "field_path": _workflow_field_path(first_error, workflow_issue),
                "suggested_next_step": (
                    "Use this tool's nested write schema, correct the named Workflow field, "
                    "and send one corrected call. Do not copy workflow_get read-projection "
                    "fields into a mutation."
                ),
            }
        )
    return _invalid_request_failure(field_path=_pydantic_field_path(first_error))


def _invalid_request_failure(*, field_path: str) -> OperationFailure:
    return OperationFailure.model_validate(
        {
            "code": ProductFailureCode.INVALID_REQUEST,
            "summary": "The tool request contains an unsupported or invalid field.",
            "retryable": False,
            "field_path": field_path,
            "suggested_next_step": (
                "Correct the named field using the tool's current input schema and send one "
                "corrected call."
            ),
        }
    )


def _workflow_input_issue(error: Mapping[str, Any]) -> WorkflowValidationIssue | None:
    context = error.get("ctx")
    cause = context.get("error") if isinstance(context, dict) else None
    if not isinstance(cause, WorkflowInputError) or not cause.issues:
        return None
    return cause.issues[0]


def _workflow_field_path(
    error: Mapping[str, Any],
    issue: WorkflowValidationIssue,
) -> str:
    prefix = _pydantic_field_path(error)
    suffix = issue.path.removeprefix("$").removeprefix(".")
    return ".".join(part for part in (prefix, suffix) if part)


def _pydantic_field_path(error: Mapping[str, Any]) -> str:
    location = error.get("loc")
    if not isinstance(location, tuple):
        return "arguments"
    rendered = ".".join(str(part) for part in location)
    return rendered or "arguments"


__all__ = [
    "OperatorToolInvocationResult",
    "invoke_operator_tool",
    "reject_operator_tool_request",
    "uncertain_operator_tool_result",
]
