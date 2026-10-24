---
name: implement-spec
description: "Implement a spec and its tickets in parallel, with OCR review and verified acceptance criteria."
disable-model-invocation: true
---

# Implement Spec

Deliver the spec on one integration branch. Carry authorized work through acceptance; ask the user when progress requires a goal or scope change, additional authorization, or resolution of a blocker you cannot remove. Treat tickets as a dependency graph: keep ready, independent work moving in parallel. The coordinator owns the run record; pass context through ticket identities, commits, and evidence paths.

**Report stalls at every stage.** Follow [stalled progress](progress.md) after two consecutive attempts produce the same failure without new evidence, or two consecutive rounds fail to narrow the problem. Report confirmed permission or external dependency blockers immediately. Continue authorized work; pause only paths requiring a user decision, subject to existing stage gates.

## Process

1. **Establish scope.** Read the project's `docs/agents/issue-tracker.md`, then complete [task discovery](task-discovery.md). Begin implementation once the first complete snapshot and relationship classification are recorded. Propose missing acceptance criteria and obtain the user's confirmation; continue independent paths.
2. **Establish the run.** Read [branches and run records](run-record.md), preserve the baseline, and create `run.json` outside the repository. Report its absolute path. Read [run resources](resource-management.md) before creating persistent resources or resuming work; keep resource details in the registry.
3. **Implement ready tickets.** Follow [implementation, review, and merging](implementation.md). Use TDD at the agreed highest observable seam, targeted tests, and typechecking. Obtain independent read-only OCR review for each ticket; retain the reviewer through its fix loop. The coordinator merges sequentially and advances the ready frontier. Reserve full formal checks for a stable candidate.
4. **Hand off stages.** Follow [stage handoff](collaboration.md) between functional implementation, performance work, and final acceptance for check close-out, reviewer continuity, and compact handoff packets.
5. **Review integration.** Follow [integration review](integration-review.md). Reconcile prior coverage against OCR's full-range inventory, including interactions, conflict resolutions, and gaps. Enter acceptance when all valid findings are resolved and affected checks pass.
6. **Verify and write back.** Follow [acceptance and handoff](acceptance.md). Complete discovery before delivery and pin the candidate commit. Use established formal checks to fill missing or invalidated evidence, retaining valid original sources. Match current criteria exactly before write-back. The optional [evidence plan](evidence-plan.md) handles mechanical correspondence; an independent reviewer judges semantic requirements.
7. **Deliver and clean up.** Once every ticket has a nonempty acceptance region, all criteria are earned, and write-back succeeds, follow the acceptance protocol to push and mark the PR ready. Process temporary resources individually. Report delivery and cleanup separately; retain resources whose state remains unknown.

## Conditional references

- **Performance work:** read [performance work](performance.md) for evidence-driven reviews and user budgets. Its legacy-record pointer covers migration when needed.
- **Query failure, context compaction, or external-state resume:** read [failure and recovery](task-discovery.md#failure-and-recovery). Distinguish first discovery from a saved complete snapshot; preserve only the local work that the recovery rules allow.
- **Waiting for agents or long checks:** use notifications or bounded waits. Update the run record on completion, blockers, or interface changes. Read detailed logs for a concrete failure and maintain host-required progress updates.
- **Creating, observing, or cleaning up sessions, services, formal jobs, or worktrees:** read [run resources](resource-management.md). Register original interface results; repair failed registration using the saved result. Short synchronous commands need only execution records.
- **Changing this skill's maintained source or installed copy:** read [maintenance and evaluation](maintenance.md). Verify the source, preserve backups, and check the actual installation mechanism, scope, and hashes before any authorized synchronization. Unproven benefits remain a pilot.

Use each protocol's completion criteria. Keep unverified executable requirements unchecked. Scope and cost changes remain subject to user authorization and host approval.
