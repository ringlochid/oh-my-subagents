from __future__ import annotations

from typing import cast

from openai_codex import AsyncCodex
from openai_codex.generated.v2_all import ModelListResponse

from oh_my_subagents.integrations.codex.model_options import (
    read_codex_operator_model_options,
)


class _FakeCodex:
    def __init__(self, response: ModelListResponse) -> None:
        self.response = response
        self.was_closed = False

    async def models(self, *, include_hidden: bool = False) -> ModelListResponse:
        assert include_hidden is False
        return self.response

    async def close(self) -> None:
        self.was_closed = True


async def test_codex_model_options_map_visible_provider_catalog() -> None:
    response = ModelListResponse.model_validate(
        {
            "data": [
                {
                    "defaultReasoningEffort": "medium",
                    "description": "Efficient model for high-volume work.",
                    "displayName": "GPT-5.6 Luna",
                    "hidden": False,
                    "id": "gpt-5.6-luna",
                    "isDefault": False,
                    "model": "gpt-5.6-luna",
                    "supportedReasoningEfforts": [
                        {"reasoningEffort": "low", "description": "Lower latency."},
                        {"reasoningEffort": "medium", "description": "Balanced."},
                    ],
                }
            ],
            "nextCursor": None,
        }
    )
    client = _FakeCodex(response)

    result = await read_codex_operator_model_options(
        client_factory=lambda _config: cast(AsyncCodex, client),
    )

    assert result is not None
    assert [option.model_dump(mode="json") for option in result] == [
        {
            "model": "gpt-5.6-luna",
            "display_name": "GPT-5.6 Luna",
            "description": "Efficient model for high-volume work.",
            "supported_efforts": ["low", "medium"],
            "is_default": False,
        }
    ]
    assert client.was_closed is True


async def test_codex_model_options_fail_closed_on_incomplete_page() -> None:
    response = ModelListResponse.model_validate(
        {
            "data": [],
            "nextCursor": "more-models",
        }
    )
    client = _FakeCodex(response)

    result = await read_codex_operator_model_options(
        client_factory=lambda _config: cast(AsyncCodex, client),
    )

    assert result is None
    assert client.was_closed is True
