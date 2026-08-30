from __future__ import annotations

from types import SimpleNamespace

import openai_codex.client as codex_client_module
import pytest
from claude_agent_sdk import ClaudeAgentOptions
from claude_agent_sdk._internal.transport import subprocess_cli as claude_subprocess_module

import oh_my_subagents.integrations.claude.isolation as claude_isolation_module
import oh_my_subagents.integrations.codex.isolation as codex_isolation_module
from oh_my_subagents.integrations.provider_process_launch import (
    configure_claude_process_launch,
    configure_codex_process_launch,
    provider_process_creation_flags,
)

_CREATE_NO_WINDOW = 0x08000000
_CODEX_SUBPROCESS_ATTRIBUTE = "subprocess"
_CLAUDE_ANYIO_ATTRIBUTE = "anyio"


def test_codex_process_launch_adds_no_window_without_replacing_other_module_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []
    pipe = object()

    def popen(*_args: object, **kwargs: object) -> object:
        calls.append(kwargs)
        return object()

    subprocess_module = SimpleNamespace(Popen=popen, PIPE=pipe)
    monkeypatch.setattr(codex_client_module, "subprocess", subprocess_module)

    configure_codex_process_launch(platform_name="win32")
    configured_module = getattr(codex_client_module, _CODEX_SUBPROCESS_ATTRIBUTE)
    configured_module.Popen(["codex", "app-server"], creationflags=0x20)
    configure_codex_process_launch(platform_name="win32")

    assert calls == [{"creationflags": _CREATE_NO_WINDOW | 0x20}]
    assert configured_module.PIPE is pipe
    assert getattr(codex_client_module, _CODEX_SUBPROCESS_ATTRIBUTE) is configured_module


@pytest.mark.asyncio
async def test_claude_process_launch_adds_no_window_without_replacing_other_module_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []
    to_thread = object()

    async def open_process(*_args: object, **kwargs: object) -> object:
        calls.append(kwargs)
        return object()

    anyio_module = SimpleNamespace(open_process=open_process, to_thread=to_thread)
    monkeypatch.setattr(claude_subprocess_module, "anyio", anyio_module)

    configure_claude_process_launch(platform_name="win32")
    configured_module = getattr(claude_subprocess_module, _CLAUDE_ANYIO_ATTRIBUTE)
    result = await configured_module.open_process(["claude", "-v"], creationflags=0x40)
    configure_claude_process_launch(platform_name="win32")

    assert result is not None
    assert calls == [{"creationflags": _CREATE_NO_WINDOW | 0x40}]
    assert configured_module.to_thread is to_thread
    assert getattr(claude_subprocess_module, _CLAUDE_ANYIO_ATTRIBUTE) is configured_module


def test_provider_process_launch_is_unchanged_off_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    codex_subprocess = SimpleNamespace()
    claude_anyio = SimpleNamespace()
    monkeypatch.setattr(codex_client_module, "subprocess", codex_subprocess)
    monkeypatch.setattr(claude_subprocess_module, "anyio", claude_anyio)

    configure_codex_process_launch(platform_name="linux")
    configure_claude_process_launch(platform_name="linux")

    assert getattr(codex_client_module, _CODEX_SUBPROCESS_ATTRIBUTE) is codex_subprocess
    assert getattr(claude_subprocess_module, _CLAUDE_ANYIO_ATTRIBUTE) is claude_anyio
    assert provider_process_creation_flags(platform_name="linux") == 0
    assert provider_process_creation_flags(platform_name="win32") == _CREATE_NO_WINDOW


def test_codex_client_builder_configures_background_process_launch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    sentinel = object()
    monkeypatch.setattr(
        codex_isolation_module,
        "configure_codex_process_launch",
        lambda: events.append("configure"),
    )
    monkeypatch.setattr(codex_isolation_module, "CodexClient", lambda *_args, **_kwargs: sentinel)

    client = codex_isolation_module.build_codex_client(lambda _method, _params: {})

    assert client is sentinel
    assert events == ["configure"]


def test_claude_client_builder_configures_background_process_launch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    sentinel = object()
    monkeypatch.setattr(
        claude_isolation_module,
        "configure_claude_process_launch",
        lambda: events.append("configure"),
    )
    monkeypatch.setattr(
        claude_isolation_module,
        "ClaudeSDKClient",
        lambda _options: sentinel,
    )

    client = claude_isolation_module.build_claude_client(ClaudeAgentOptions())

    assert client is sentinel
    assert events == ["configure"]
