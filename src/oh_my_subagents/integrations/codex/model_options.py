from __future__ import annotations

import asyncio
from collections.abc import Callable

from openai_codex import AsyncCodex, CodexConfig

from oh_my_subagents.integrations.provider_process_launch import configure_codex_process_launch
from oh_my_subagents.operator.tools.model_options import OperatorProviderModelOption
from oh_my_subagents.platform.provider_environment import provider_subprocess_environment_overrides

_MODEL_CATALOG_TIMEOUT_SECONDS = 10.0
type CodexModelCatalogClientFactory = Callable[[CodexConfig], AsyncCodex]


async def read_codex_operator_model_options(
    *,
    client_factory: CodexModelCatalogClientFactory = AsyncCodex,
) -> tuple[OperatorProviderModelOption, ...] | None:
    """Read one complete visible model catalog from the configured Codex identity."""

    configure_codex_process_launch()
    try:
        client = client_factory(
            CodexConfig(
                env=provider_subprocess_environment_overrides(),
                experimental_api=True,
            )
        )
    except Exception:
        return None

    response = None
    did_fail = False
    try:
        response = await asyncio.wait_for(
            client.models(include_hidden=False),
            timeout=_MODEL_CATALOG_TIMEOUT_SECONDS,
        )
    except Exception:
        did_fail = True
    finally:
        try:
            await asyncio.wait_for(
                client.close(),
                timeout=_MODEL_CATALOG_TIMEOUT_SECONDS,
            )
        except Exception:
            did_fail = True

    if did_fail or response is None or response.next_cursor is not None:
        return None
    try:
        return tuple(
            OperatorProviderModelOption(
                model=model.model,
                display_name=model.display_name,
                description=model.description,
                supported_efforts=tuple(
                    option.reasoning_effort.value for option in model.supported_reasoning_efforts
                ),
                is_default=model.is_default,
            )
            for model in response.data
            if not model.hidden
        )
    except Exception:
        return None


__all__ = ["CodexModelCatalogClientFactory", "read_codex_operator_model_options"]
