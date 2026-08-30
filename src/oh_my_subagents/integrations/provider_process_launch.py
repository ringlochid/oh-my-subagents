from __future__ import annotations

import sys
from typing import Any

import openai_codex.client as codex_client_module
from claude_agent_sdk._internal.transport import subprocess_cli as claude_subprocess_module

_CREATE_NO_WINDOW = 0x08000000
_CODEX_SUBPROCESS_ATTRIBUTE = "subprocess"
_CLAUDE_ANYIO_ATTRIBUTE = "anyio"


class _NoWindowSubprocessModule:
    def __init__(self, subprocess_module: Any) -> None:
        self._subprocess_module = subprocess_module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._subprocess_module, name)

    def Popen(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802 - SDK module API
        kwargs["creationflags"] = _CREATE_NO_WINDOW | int(kwargs.get("creationflags", 0))
        return self._subprocess_module.Popen(*args, **kwargs)


class _NoWindowAnyioModule:
    def __init__(self, anyio_module: Any) -> None:
        self._anyio_module = anyio_module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._anyio_module, name)

    async def open_process(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["creationflags"] = _CREATE_NO_WINDOW | int(kwargs.get("creationflags", 0))
        return await self._anyio_module.open_process(*args, **kwargs)


def configure_codex_process_launch(*, platform_name: str | None = None) -> None:
    """Keep the pinned Codex SDK app-server off the Windows desktop."""

    if provider_process_creation_flags(platform_name=platform_name) == 0:
        return
    current_module = getattr(codex_client_module, _CODEX_SUBPROCESS_ATTRIBUTE)
    if isinstance(current_module, _NoWindowSubprocessModule):
        return
    setattr(
        codex_client_module,
        _CODEX_SUBPROCESS_ATTRIBUTE,
        _NoWindowSubprocessModule(current_module),
    )


def configure_claude_process_launch(*, platform_name: str | None = None) -> None:
    """Keep the pinned Claude SDK preflight and session off the Windows desktop."""

    if provider_process_creation_flags(platform_name=platform_name) == 0:
        return
    current_module = getattr(claude_subprocess_module, _CLAUDE_ANYIO_ATTRIBUTE)
    if isinstance(current_module, _NoWindowAnyioModule):
        return
    setattr(
        claude_subprocess_module,
        _CLAUDE_ANYIO_ATTRIBUTE,
        _NoWindowAnyioModule(current_module),
    )


def provider_process_creation_flags(*, platform_name: str | None = None) -> int:
    """Return the native Windows flag for a background provider process."""

    resolved_platform = platform_name or sys.platform
    return _CREATE_NO_WINDOW if resolved_platform == "win32" else 0


__all__ = [
    "configure_claude_process_launch",
    "configure_codex_process_launch",
    "provider_process_creation_flags",
]
