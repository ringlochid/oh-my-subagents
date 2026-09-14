---
title: Local subagent orchestration for Codex and Claude
description: Run durable Codex and Claude agent teams locally. Reuse team definitions, persist delegated work, recover from interruptions, and inspect one accountable result.
---

# Durable AI teams for Codex and Claude

**Turn ad-hoc subagents into durable, accountable AI teams.**

Oh My Subagents is a local runtime for subagent orchestration with Codex and Claude. Build a reusable team, give its lead one concrete mission, and follow the work in a visual Console. The controller records delegation, waits, returned evidence, and one completed or blocked Result.

[Install and run your first team](start/getting-started.md){ .md-button .md-button--primary } [Explore the source](https://github.com/ringlochid/oh-my-subagents){ .md-button }

## Start with your provider

- [Run a Codex agent team](guides/codex-agent-teams.md) — configure Codex, start a coding mission, and inspect the returned work.
- [Run a Claude agent team](guides/claude-agent-teams.md) — configure Claude, check sandbox prerequisites, and start a research or coding team.
- [Use independent code review](guides/multi-agent-code-review.md) — separate implementation, review, repair, and integrated verification.
- [Recover interrupted agent work](guides/recover-interrupted-agents.md) — inspect the original run and continue from committed controller state.

## Why Oh My Subagents

- **Reuse explicit responsibility trees** instead of recreating roles and prompts for every job.
- **Delegate without polling** while the runtime commits Assignments, persists waits, supervises returns, and continues the parent.
- **Recover from committed state** after a provider interruption, browser closure, or controller restart.
- **Return one accountable Result** after the Task lead inspects the team's Checkpoints, evidence, and referenced files.

![How OMS delegates work, persists a parent wait, and collects the complete team's returns](assets/oms-how-it-works-v8.png){ loading=lazy decoding=async fetchpriority=low }

[Watch the Console tutorial](https://www.youtube.com/watch?v=-prDEZYpx9M) to see the product in use.

## Install locally

For a fresh installation with Python 3.12 or newer:

```bash
pipx install oh-my-subagents
oms init
oms service install
```

Open `http://127.0.0.1:18125/`. Linux, macOS 13+, and Windows 11 x64 are supported; SQLite is the default. The [installation guide](start/getting-started.md) covers provider authentication, platform requirements, and existing installations.

## Start here

- [Getting started](start/getting-started.md) — install Oh My Subagents, configure a provider, and complete a first developer or researcher run.
- [Starter team catalog](../examples/workflows/README.md) — choose among the eight installed Workflows using realistic missions and expected deliverables.

## Understand the product

- [Workflows and teams](concepts/workflows-and-teams.md) — understand responsibility trees, Members, providers, capabilities, and adaptive work.
- [Runtime and Results](concepts/runtime-and-results.md) — understand Tasks, Assignments, Checkpoints, and the lead's final Result.
- [Workspace and files](concepts/workspace-and-files.md) — understand the shared workspace, loose file references, notes, and deliverables.

## Build and run teams

- [Author a Workflow](guides/author-a-workflow.md) — start from a Starter, shape responsibilities in Workflow Studio or with the Operator, validate, and publish.
- [Run and operate](guides/run-and-operate.md) — start work, read the run view, respond to allowed waits, and use legal controls.
- [Console and Operator](guides/console-and-operator.md) — visually edit and publish teams, inspect live work and Results, or use the separate conversational Operator for the same product operations.
- [Migrate from Banksia](guides/migrate-from-banksia.md) — copy an existing installation into canonical OMS state.

## Configure and integrate

- [Configuration reference](reference/configuration.md) — configure SQLite or PostgreSQL, providers, workspace defaults, sandboxing, and Operator.
- [Workflow definition reference](reference/workflows/README.md) — use the public JSON/YAML schema and field contract.
- [CLI reference](reference/cli.md) — automate local setup and product operations.
- [HTTP API](reference/http-api.md) — integrate through the loopback product API.
- [Controller tools](reference/controller-tools.md) — understand the exact Task-member and Operator tool surfaces.

## Fix a problem

- [Troubleshooting](help/troubleshooting.md) — diagnose initialization, database, provider, controller, Workflow, and recovery problems.
- [Report an issue](https://github.com/ringlochid/oh-my-subagents/issues) — include the smallest redacted evidence that reproduces the problem.

## Contribute

- [Contributing](../CONTRIBUTING.md) — prepare a source checkout, follow repository owners, work in a bounded slice, and report executable proof.
- [Maintainer verification](maintainers/README.md) — run the repository's quality, contract, and release-readiness checks.

## Project and licensing

Oh My Subagents is maintained by [Leo Zhang and contributors](https://github.com/ringlochid/oh-my-subagents/graphs/contributors). The core is [MIT licensed](../LICENSE). The visual Console contains n8n-derived material and uses the [Sustainable Use License](../console/LICENSE); see its [attribution notice](../console/NOTICE).
