---
title: Recover interrupted AI agent work in Oh My Subagents
description: Inspect an interrupted OMS run, check controller and provider readiness, and recover from committed state without confusing process completion with task success.
---

# Recover interrupted agent work

Oh My Subagents stores controller records outside an individual provider conversation. Closing a browser, losing a provider process, and restarting the controller have different effects. Begin with the existing run and its committed state before starting replacement work.

## Identify what stopped

| Interruption | First action |
| --- | --- |
| Browser tab closed | Reopen the Console and select the existing run. The browser does not own runtime supervision. |
| Terminal closed while using the managed service | Check the service. The native service can keep the controller running. |
| Foreground `oms serve` process stopped | Start `oms serve` again with the same configuration and database. |
| Provider process interrupted | Inspect current run Activity, provider readiness, and the controls the controller offers. |
| Controller restarted | Allow startup recovery to reconcile committed state, then refresh the existing run. |

## Check the controller

For a managed-service installation:

```bash
oms service status
oms status
oms service logs --lines 100
```

If the installed service is stopped, use `oms service start`. If it reports **Needs attention**, inspect the logs and resolve the reported problem. A listener alone does not establish that the native service owns a ready controller.

For a foreground installation, run `oms serve` with the original configuration. Preserve the same database, workspace, and provider settings. Creating a fresh controller database does not recover the earlier run.

## Reopen the existing run

Open `http://127.0.0.1:18125/`, select the run in **Runs**, and inspect **Team**, **Current plan**, and **Activity**.

The controller audits committed runtime sources on startup and reconciles work that can legally continue. A delegated Wave records the parent's wait and the child Assignments; the parent becomes eligible to continue after the complete Wave settles.

Use the controls currently offered by the Console:

- **Resume** is for eligible paused work.
- Respond to a Human Request when input is required.
- Inspect a blocked Result and its explanation before deciding what new work is appropriate.

Refresh when another event changes the run. Do not assume that every interruption offers the same retry or resume operation.

## Check the provider when needed

```bash
oms providers status
```

Use `oms providers check codex` or `oms providers check claude` for the configured route. Address authentication, unavailable models, or sandbox prerequisites using [configuration](../reference/configuration.md) and [troubleshooting](../help/troubleshooting.md).

## Confirm recovery from evidence

A recovered controller should be ready and show the original run and its accepted history. Follow new Activity and inspect the lead's eventual completed or blocked Result. A successful provider exit is insufficient to establish Task success.

OMS preserves controller state, not an exact snapshot of every external side effect or workspace file. A command may have written files before it was interrupted. Inspect the current files and relevant application state before repeating work that could have effects twice.

For a controlled recovery exercise, use a disposable project and a low-impact task. Record the run identity, current Activity, and workspace state; stop and restart the controller through its supported lifecycle; then check the same run and files. This is a suggested exercise, not a reported successful test of your installation.

For routine operation and the exact meaning of pause, resume, cancellation, and Result, read [Run and operate](run-and-operate.md).
