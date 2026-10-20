---
name: implement-spec
description: "Implement a spec and its tickets in parallel, with OCR review and verified acceptance criteria."
disable-model-invocation: true
---

# Implement Spec

Deliver the spec on one integration branch. Carry authorized work through acceptance; ask the user when progress requires a goal or scope change, additional authorization, or resolution of a blocker you cannot remove. Treat tickets as a dependency graph: keep ready, independent work moving in parallel. The coordinator owns the run record; pass context through ticket identities, commits, and evidence paths.

**停滞汇报适用于全部阶段。** 同一问题连续两次尝试仍出现相同失败且无新证据，或连续两轮行动未缩小问题范围时，立即按[停滞汇报](progress.md)报告；确认权限或外部依赖阻塞时立即报告。汇报后继续授权范围内可推进的工作；需要人类决策时，仅暂停受影响路径，并遵守该阶段的既有门槛。

## Process

1. **Establish scope.** Read the project's `docs/agents/issue-tracker.md`, then complete [task discovery](task-discovery.md). Begin implementation once the first complete snapshot and relationship classification are recorded. Propose missing acceptance criteria and obtain the user's confirmation; continue independent paths.
2. **Establish the run.** Read [branches and run records](run-record.md), preserve the baseline, and create `run.json` outside the repository. Report its absolute path. Read [run resources](resource-management.md) before creating persistent resources or resuming work; keep resource details in the registry.
3. **Implement ready tickets.** Follow [implementation, review, and merging](implementation.md). Use TDD at the agreed highest observable seam, targeted tests, and typechecking. Obtain independent read-only OCR review for each ticket; retain the reviewer through its fix loop. The coordinator merges sequentially and advances the ready frontier. Reserve full formal checks for a stable candidate.
4. **Hand off stages.** 按[阶段交接](collaboration.md)移交功能、性能或最终验收阶段；该协议规定检查收尾、reviewer 延续和紧凑交接记录。
5. **Review integration.** Follow [integration review](integration-review.md). Reconcile prior coverage against OCR's full-range inventory, including interactions, conflict resolutions, and gaps. Enter acceptance when all valid findings are resolved and affected checks pass.
6. **Verify and write back.** Follow [acceptance and handoff](acceptance.md). Complete discovery before delivery and pin the candidate commit. Use established formal checks to fill missing or invalidated evidence, retaining valid original sources. Match current criteria exactly before write-back. The optional [evidence plan](evidence-plan.md) handles mechanical correspondence; an independent reviewer judges semantic requirements.
7. **Deliver and clean up.** Once every ticket has a nonempty acceptance region, all criteria are earned, and write-back succeeds, follow the acceptance protocol to push and mark the PR ready or close work directly. Process temporary resources individually. Report delivery and cleanup separately; retain resources whose state remains unknown.

## Conditional references

- **性能工作：** 读取[性能协议](performance.md)，按证据复盘并遵守用户预算；恢复旧阶段记录时按其中的条件指针加载迁移规则。
- **Query failure, context compaction, or external-state resume:** read [failure and recovery](task-discovery.md#failure-and-recovery). Distinguish first discovery from a saved complete snapshot; preserve only the local work that the recovery rules allow.
- **Waiting for agents or long checks:** use notifications or bounded waits. Update the run record on completion, blockers, or interface changes. Read detailed logs for a concrete failure and maintain host-required progress updates.
- **Creating, observing, or cleaning up sessions, services, formal jobs, or worktrees:** read [run resources](resource-management.md). Register original interface results; repair failed registration using the saved result. Short synchronous commands need only execution records.
- **Changing this skill's maintained source or installed copy:** read [maintenance and evaluation](maintenance.md). Verify the source, preserve backups, and check the actual installation mechanism, scope, and hashes before any authorized synchronization. Unproven benefits remain a pilot.

Use each protocol's completion criteria. Keep unverified executable requirements unchecked. Scope and cost changes remain subject to user authorization and host approval.
