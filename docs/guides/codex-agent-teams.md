---
title: Codex subagent orchestration with persistent AI teams
description: Set up Codex in Oh My Subagents, choose a reusable team, run a concrete task, and inspect the lead's result and persistent execution history.
---

# Run a Codex agent team with Oh My Subagents

Oh My Subagents adds a local controller around Codex-backed work. You publish a reusable team, give its lead a concrete mission, and inspect the team's progress and final Result in the browser. OMS records delegation, waits, and returned Checkpoints outside an individual provider conversation.

Use this guide when a task benefits from independent implementation, review, or research. A one-Member Workflow is also valid when delegation would add little value.

## Install and select Codex

You need Python 3.12 or newer, a supported Linux, macOS 13+, or Windows 11 x64 host, and a Codex authentication path. Use a local project directory as the workspace. The [installation guide](../start/getting-started.md) covers platform details and existing-installation handling.

For a fresh installation:

```bash
pipx install oh-my-subagents
oms init
```

Run initialization from your project directory. Select **Codex** for Task work and follow the authentication prompts. Operator is optional: it is the separate conversational interface for controlling OMS, rather than the default provider for the team.

For an existing OMS installation, use `oms setup` to select or change the Task provider. Then inspect the configured route:

```bash
oms providers status
oms providers check codex
```

The check is a bounded provider diagnostic. A configured provider still needs to be authenticated and able to run the selected model. Use the actual model choices offered by your installation; an explicit unavailable model does not silently fall back.

## Start the controller

```bash
oms service install
oms service status
```

Open `http://127.0.0.1:18125/`. Alternatively, use `oms serve` to keep the controller in a foreground terminal. With the managed service, the controller can continue supervising work after that terminal closes.

## Give the team one concrete mission

In **Runs → New run**, select `production-feature-delivery`. The installed Starters omit provider overrides, so they use the configured default Task provider.

Here is a sample mission to adapt to an existing repository:

> Add CSV export to the existing search results page. Preserve the current filters and permissions.
> Establish the API and file-format contract, implement the change, independently review escaping
> and access control, run the relevant tests, repair consequential findings, and return the result
> with references to the changed files and verification evidence. Do not deploy the change.

This is an example input, not a claim that a run has already succeeded. Narrow its scope and permissions to match your project before starting.

The team is a responsibility hierarchy. Its Managers decide whether the actual work should proceed sequentially, in parallel, or through review-and-repair iterations. Publishing a team does not freeze that schedule.

## Check the outcome

1. Follow **Team**, **Current plan**, and **Activity** for ownership and meaningful updates.
2. Answer a Human Request if an authorized Member needs your input.
3. Read the lead's **Result**, including whether it completed or is blocked.
4. Open referenced files in your workspace and inspect the actual change and test evidence.

A child finishing is evidence for its parent. It does not alone establish that the whole task succeeded. File references point to ordinary workspace files, so use version control when you need to preserve their exact bytes.

## Continue from here

- [Use independent implementation and review](multi-agent-code-review.md) for a concrete review loop.
- [Recover interrupted work](recover-interrupted-agents.md) explains controller restart and its limits.
- [Choose a Starter team](../../examples/workflows/README.md) for research, recovery, migration, or security work.
- [Configure providers and sandboxing](../reference/configuration.md) before changing access or provider overrides.
