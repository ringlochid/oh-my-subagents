from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from oh_my_subagents.operator.prompt import read_operator_system_prompt
from oh_my_subagents.operator.tools import OperatorToolName, build_operator_tools
from oh_my_subagents.operator.tools.model_options import OperatorProviderModelOption
from tests.helpers.product_surface import product_dispatch_dependencies


@asynccontextmanager
async def _unexpected_session() -> AsyncIterator[AsyncSession]:
    raise AssertionError("authoring-options proof must not open a database session")
    yield  # pragma: no cover


async def test_authoring_options_include_lazy_codex_model_catalog(tmp_path: Path) -> None:
    dependencies = product_dispatch_dependencies(tmp_path)
    read_count = 0

    async def read_codex_models() -> tuple[OperatorProviderModelOption, ...]:
        nonlocal read_count
        read_count += 1
        return (
            OperatorProviderModelOption(
                model="gpt-5.6-luna",
                display_name="GPT-5.6 Luna",
                description="Efficient model for high-volume work.",
                supported_efforts=("none", "low", "medium", "high", "xhigh", "max"),
                is_default=False,
            ),
        )

    tools = build_operator_tools(
        settings=dependencies.settings,
        session_factory=_unexpected_session,
        dispatch_dependencies=dependencies,
        codex_model_options_reader=read_codex_models,
    )

    result = await next(
        tool for tool in tools if tool.name is OperatorToolName.WORKFLOW_AUTHORING_OPTIONS
    ).call({})

    assert read_count == 1
    assert result["codex_models"] == [
        {
            "model": "gpt-5.6-luna",
            "display_name": "GPT-5.6 Luna",
            "description": "Efficient model for high-volume work.",
            "supported_efforts": ["none", "low", "medium", "high", "xhigh", "max"],
            "is_default": False,
        }
    ]
    assert result["claude_models"] is None


def test_operator_prompt_teaches_lean_reference_aware_authoring() -> None:
    prompt = " ".join(read_operator_system_prompt().split())

    for required_guidance in (
        "Use the smallest sufficient action sequence",
        "create the smallest reusable responsibility tree",
        "treat it as a structural design reference",
        "call `workflow_authoring_options`",
        "Never invent or silently substitute a model",
    ):
        assert required_guidance in prompt
