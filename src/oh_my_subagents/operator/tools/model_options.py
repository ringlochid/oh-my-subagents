from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from oh_my_subagents.workflows.authoring_contracts import WorkflowAuthoringOptions


class OperatorProviderModelOption(BaseModel):
    """One provider-reported model that Operator may author explicitly."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model: Annotated[str, Field(min_length=1, max_length=255)]
    display_name: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str, Field(max_length=2048)]
    supported_efforts: Annotated[tuple[str, ...], Field(max_length=16)]
    is_default: bool


class OperatorWorkflowAuthoringOptions(WorkflowAuthoringOptions):
    """Operator-private authoring projection with transient provider model choices."""

    codex_models: (
        Annotated[
            tuple[OperatorProviderModelOption, ...],
            Field(max_length=100),
        ]
        | None
    ) = None
    claude_models: (
        Annotated[
            tuple[OperatorProviderModelOption, ...],
            Field(max_length=100),
        ]
        | None
    ) = None


def map_operator_workflow_authoring_options(
    source: WorkflowAuthoringOptions,
    *,
    codex_models: tuple[OperatorProviderModelOption, ...] | None,
    claude_models: tuple[OperatorProviderModelOption, ...] | None = None,
) -> OperatorWorkflowAuthoringOptions:
    """Extend public authoring truth without changing its HTTP contract."""

    return OperatorWorkflowAuthoringOptions.model_validate(
        {
            **source.model_dump(mode="json"),
            "codex_models": codex_models,
            "claude_models": claude_models,
        }
    )


__all__ = [
    "OperatorProviderModelOption",
    "OperatorWorkflowAuthoringOptions",
    "map_operator_workflow_authoring_options",
]
