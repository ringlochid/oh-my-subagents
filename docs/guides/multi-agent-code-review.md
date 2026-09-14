---
title: Multi-agent code review with independent implementation and verification
description: Run a coding task in OMS with explicit ownership, independent review, evidence-backed repair, and one final result. Includes a concrete mission template.
---

# Independent code review with an AI agent team

Oh My Subagents can keep implementation, review, and integration under explicit responsibilities while one lead owns the final Result. The runtime preserves delegated work and returned Checkpoints; the team uses that evidence to decide what needs repair or further verification.

Use this pattern for a consequential change with distinct failure modes or multiple implementation boundaries. For a small, tightly coupled edit, a simpler Workflow may be more efficient.

## Prepare a bounded task

Complete [Codex setup](codex-agent-teams.md) or [Claude setup](claude-agent-teams.md), then inspect the repository and choose a workspace. Commit or otherwise preserve the starting state using your normal version-control workflow.

Write down the intended behavior, files or boundaries in scope, compatibility constraints, relevant tests, and whether publishing or deployment is permitted. Giving several agents the same vague instruction does not create independent verification.

## Choose and inspect the team

In **Runs → New run**, choose `production-feature-delivery`. Before running unfamiliar work, inspect the published team in **Workflows** and read its responsibilities and capability grants.

The Starter provides contract ownership, delivery coordination, and independent integration verification. Its Managers choose actual Assignments and work patterns at runtime. The [Starter catalog](../../examples/workflows/README.md) explains when each installed team is useful.

## Supply a concrete review brief

Adapt this sample mission to a real project:

> Add CSV export for the current search results, respecting the active filters and existing access
> checks. Keep implementation ownership separate from review. Review formula injection, quoting,
> Unicode, empty results, and unauthorized access. Run the project's relevant tests. Return each
> actionable finding with a location, reproduction or reasoning, impact, and expected behavior.
> Repair accepted findings and independently verify the repaired behavior. Return one final
> result with changed-file and test-evidence references. Do not commit, push, or deploy.

The requested workflow is:

1. Establish the supported behavior and scope.
2. Assign implementation and independently useful review responsibilities.
3. Collect the complete returned evidence.
4. Turn accepted findings into bounded repair work.
5. Verify the integrated change and return the lead's Result.

This describes the mission's acceptance conditions. It is not a fixed graph schedule or a guarantee that a specific run will succeed. Review findings can legitimately produce a blocked Result.

## Evaluate the returned work

Read the final Result alongside the actual diff and referenced reports. Check that findings were addressed or explicitly resolved, that the tests exercised the changed behavior, and that unresolved risks remain visible.

Checkpoints communicate work between teammates. They do not replace the underlying files, tests, or your release decision. OMS records navigation references rather than immutable file snapshots, so preserve important deliverables in version control.

For a mixed-provider authoring example, inspect the maintained [advanced reviewed-code-change definition](../../examples/workflows/advanced-reviewed-code-change.yaml). It is an advanced reference, not an installed Starter. Import creates a draft; validate and publish it deliberately after reviewing provider, network, sandbox, and capability choices.

## Keep the collaboration useful

Assign disjoint editing areas when concurrent changes could conflict. Independent review helps when it brings a separate hypothesis, test oracle, or risk analysis; duplicating the entire task across every Member adds coordination cost.

Use [run controls and steering](run-and-operate.md) for new context during execution. Use [interruption recovery](recover-interrupted-agents.md) when the controller or provider stops unexpectedly.
