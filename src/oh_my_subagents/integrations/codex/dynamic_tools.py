from __future__ import annotations

import asyncio
import json
import threading
from collections.abc import Sequence
from concurrent.futures import Future

from openai_codex.models import JsonObject

from oh_my_subagents.operator.provider import OperatorProviderUnavailableError
from oh_my_subagents.operator.tools import OperatorTool
from oh_my_subagents.operator.tools.execution import (
    OperatorToolInvocationResult,
    invoke_operator_tool,
    reject_operator_tool_request,
    uncertain_operator_tool_result,
)

_DYNAMIC_TOOL_METHOD = "item/tool/call"


class CodexDynamicToolBridge:
    """Bridge sync SDK callbacks while retaining the real async task for cleanup."""

    def __init__(
        self,
        *,
        loop: asyncio.AbstractEventLoop,
        tools: Sequence[OperatorTool],
    ) -> None:
        self._loop = loop
        self._tools = {tool.name.value: tool for tool in tools}
        self._pending_tasks: set[asyncio.Task[JsonObject]] = set()
        self._lock = threading.Lock()
        self._is_active = True

    def __call__(self, method: str, params: JsonObject | None) -> JsonObject:
        if method != _DYNAMIC_TOOL_METHOD:
            return _deny_server_request(method)
        result: Future[JsonObject] = Future()
        with self._lock:
            if not self._is_active:
                return _render_tool_result(uncertain_operator_tool_result())
            try:
                self._loop.call_soon_threadsafe(self._start_tool_call, params, result)
            except RuntimeError:
                return _render_tool_result(uncertain_operator_tool_result())
        try:
            return result.result()
        except BaseException:
            return _render_tool_result(uncertain_operator_tool_result())

    def _start_tool_call(
        self,
        params: JsonObject | None,
        result: Future[JsonObject],
    ) -> None:
        with self._lock:
            if not self._is_active:
                result.set_result(_render_tool_result(uncertain_operator_tool_result()))
                return
            task = self._loop.create_task(self._call_tool(params))
            self._pending_tasks.add(task)
        task.add_done_callback(lambda completed: self._finish_tool_call(completed, result))

    def _finish_tool_call(
        self,
        task: asyncio.Task[JsonObject],
        result: Future[JsonObject],
    ) -> None:
        with self._lock:
            self._pending_tasks.discard(task)
        try:
            response = task.result()
        except BaseException:
            response = _render_tool_result(uncertain_operator_tool_result())
        result.set_result(response)

    async def _call_tool(self, params: JsonObject | None) -> JsonObject:
        if params is None:
            return _render_tool_result(reject_operator_tool_request(field_path="arguments"))
        if params.get("namespace") is not None:
            return _render_tool_result(reject_operator_tool_request(field_path="namespace"))
        tool_name = params.get("tool")
        if not isinstance(tool_name, str):
            return _render_tool_result(reject_operator_tool_request(field_path="tool"))
        tool = self._tools.get(tool_name)
        if tool is None:
            return _render_tool_result(reject_operator_tool_request(field_path="tool"))
        return _render_tool_result(await invoke_operator_tool(tool, params.get("arguments")))

    async def deactivate(self) -> None:
        with self._lock:
            self._is_active = False
            pending = tuple(self._pending_tasks)
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)


def _deny_server_request(method: str) -> JsonObject:
    if method in {
        "applyPatchApproval",
        "execCommandApproval",
        "item/commandExecution/requestApproval",
        "item/fileChange/requestApproval",
    }:
        return {"decision": "cancel"}
    if method == "item/permissions/requestApproval":
        return {"permissions": {}}
    if method == "item/tool/requestUserInput":
        return {"answers": {}}
    if method == "mcpServer/elicitation/request":
        return {"action": "cancel"}
    raise OperatorProviderUnavailableError("Codex requested an unsupported Operator capability")


def _render_tool_result(result: OperatorToolInvocationResult) -> JsonObject:
    rendered = json.dumps(
        result.payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return {
        "contentItems": [{"type": "inputText", "text": rendered}],
        "success": not result.is_error,
    }


__all__ = ["CodexDynamicToolBridge"]
