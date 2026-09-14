---
title: Claude agent teams with durable subagent orchestration
description: Configure Claude in Oh My Subagents, run a reusable research or coding team, check sandbox prerequisites, and inspect one accountable final result.
---

# Run a Claude agent team with Oh My Subagents

Oh My Subagents supervises Claude-backed teams through a local controller and visual Console. Reusable Workflows name responsibilities; runtime records preserve delegated Assignments, parent waits, returned Checkpoints, and the lead's Result.

This guide uses the supported Claude Task-provider adapter. You configure the team in OMS and follow its execution in the OMS Console.

## Configure Claude for Task work

Follow the [installation guide](../start/getting-started.md) for Python and operating-system prerequisites. From a suitable local workspace, initialize a fresh installation:

```bash
pipx install oh-my-subagents
oms init
```

Select **Claude** for Task work and follow its authentication prompts. For an existing controller, use `oms setup` to add or change the Task provider.

Check the configured provider before starting a team:

```bash
oms providers status
oms providers check claude
```

Choose a model supported by your authenticated route. The provider check diagnoses readiness; it does not rewrite or disable your configuration when it fails. Consult [troubleshooting](../help/troubleshooting.md) if the route cannot start.

## Check sandbox prerequisites

On Linux or WSL2, Claude Members with effective network access set to `deny` require `bubblewrap` and `socat`. On Ubuntu or Debian:

```bash
sudo apt-get install bubblewrap socat
```

These are prerequisites for that Claude sandbox configuration. The [sandbox reference](../reference/configuration.md#managed-sandbox-and-network) explains effective access and host requirements. Review each Member's provider and capability settings; grants do not inherit from its parent.

## Start a research team

Start the managed controller and open `http://127.0.0.1:18125/`:

```bash
oms service install
oms service status
```

In **Runs → New run**, choose `deep-research-and-decision-brief`. Installed Starters use the configured default Task provider unless a published Workflow explicitly overrides it.

Adapt this sample prompt:

> Decide whether this project's search index should remain embedded or move to a separate service.
> Read the repository's requirements and operational constraints. Compare current primary-source
> evidence, challenge the leading recommendation, and return one decision brief with tradeoffs,
> unresolved questions, and references to the detailed research files. Do not change the software.

The sample defines an intended research task, not an observed result. Include your actual constraints, and confirm that the team's effective capabilities support the research you want it to perform.

## Inspect the decision and evidence

Use **Team**, **Current plan**, and **Activity** to follow ownership and progress. The lead integrates child Checkpoints into one completed or blocked Result. Read the Result and open its referenced workspace files to evaluate the supporting evidence.

For coding work, choose `production-feature-delivery` and use the [independent code-review guide](multi-agent-code-review.md). For substantial experiments that need separate replication and claim review, inspect `experiment-and-replication-program` in the [Starter catalog](../../examples/workflows/README.md).

## Understand provider selection

Task-provider defaults and the optional Operator provider are separate. Choosing Claude for Operator does not automatically select it for the team's Members.

A Workflow can contain explicit per-Member provider choices. Read the [Workflow reference](../reference/workflows/README.md) before introducing mixed-provider teams, and validate and publish the edited definition before starting a new run.

If the provider or controller is interrupted, use the [recovery guide](recover-interrupted-agents.md) to inspect committed state and the legal next action.
