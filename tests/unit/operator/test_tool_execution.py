from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from oh_my_subagents.operator.tools.contracts import (
    OperatorTool,
    OperatorToolName,
    WorkflowDraftCreateInput,
)
from oh_my_subagents.operator.tools.execution import invoke_operator_tool


class _AcceptedResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    accepted: bool


async def test_invalid_workflow_write_shape_returns_safe_rejection_before_handler() -> None:
    handler_calls = 0

    async def reject_unexpected_handler_call(_request: BaseModel) -> BaseModel:
        nonlocal handler_calls
        handler_calls += 1
        return _AcceptedResult(accepted=True)

    tool = OperatorTool(
        name=OperatorToolName.WORKFLOW_DRAFT_CREATE,
        description="Create a nested Workflow draft.",
        input_model=WorkflowDraftCreateInput,
        handler=reject_unexpected_handler_call,
    )

    result = await invoke_operator_tool(
        tool,
        {
            "workflow": {
                "kind": "workflow",
                "id": "opportunity-discovery",
                "description": "Research and rank opportunities.",
                "lead_member_id": "lead",
                "members": [{"id": "lead"}],
            }
        },
    )

    assert handler_calls == 0
    assert result.is_error is True
    assert result.payload == {
        "ok": False,
        "code": "invalid_request",
        "summary": "The Workflow contains an unsupported or invalid field.",
        "retryable": False,
        "field_path": "workflow.lead",
        "suggested_next_step": (
            "Use this tool's nested write schema, correct the named Workflow field, and "
            "send one corrected call. Do not copy workflow_get read-projection fields into "
            "a mutation."
        ),
    }


async def test_unexpected_handler_failure_remains_uncertain_and_redacted() -> None:
    async def fail(_request: BaseModel) -> BaseModel:
        raise RuntimeError("private tool failure")

    tool = OperatorTool(
        name=OperatorToolName.WORKFLOW_DRAFT_CREATE,
        description="Create a nested Workflow draft.",
        input_model=WorkflowDraftCreateInput,
        handler=fail,
    )

    result = await invoke_operator_tool(
        tool,
        {
            "workflow": {
                "kind": "workflow",
                "id": "opportunity-discovery",
                "description": "Research and rank opportunities.",
                "lead": {"id": "lead"},
            }
        },
    )

    assert result.is_error is True
    assert result.payload["error"] == "operator_operation_outcome_uncertain"
    assert "private tool failure" not in str(result.payload)


async def test_handler_validation_error_is_not_misreported_as_input_rejection() -> None:
    async def fail_after_entry(_request: BaseModel) -> BaseModel:
        _AcceptedResult.model_validate({})
        raise AssertionError("unreachable")

    tool = OperatorTool(
        name=OperatorToolName.WORKFLOW_DRAFT_CREATE,
        description="Create a nested Workflow draft.",
        input_model=WorkflowDraftCreateInput,
        handler=fail_after_entry,
    )

    result = await invoke_operator_tool(
        tool,
        {
            "workflow": {
                "kind": "workflow",
                "id": "opportunity-discovery",
                "description": "Research and rank opportunities.",
                "lead": {"id": "lead"},
            }
        },
    )

    assert result.is_error is True
    assert result.payload["error"] == "operator_operation_outcome_uncertain"
    assert "ValidationError" not in str(result.payload)
