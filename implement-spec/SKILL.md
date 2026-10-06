---
name: implement-spec
description: "Implement a spec and its tickets in parallel, with OCR review and verified acceptance criteria."
disable-model-invocation: true
---

# Implement Spec

Implement the entire spec on one **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are a **task graph**, not a list of steps. The **frontier** is the set of tickets whose dependencies have landed and whose requirements are settled. Run implementer subagents in the background across that frontier.

Communicate through **context pointers** to the spec, tickets, research notes, and commits. Keep shared exploration notes outside the repo, accessible to every subagent.

## Which tracker

Read `docs/agents/issue-tracker.md` and the configuration it points to. If none has been provided, tell the user to run `/setup-matt-pocock-skills` before continuing.

## Steps

### 1. Read the task graph

先执行 [task-discovery.md](task-discovery.md) 的任务发现流程，确认查询完整性并记录任务集合及关系证据，再把任务分为可执行、等待依赖或阻塞。首次执行、会话续接及收尾均须使用该流程；查询不完整时停止全部实现。缺失依赖、循环及未决需求阻塞受影响路径。

Every ticket needs acceptance criteria before implementation. Propose missing criteria for the user's confirmation; only confirmed criteria become the ticket's requirements. Continue independent tickets while that decision is pending.

Optionally use an exploration subagent to investigate code or external documentation and save shared notes. Implementers should be able to follow those pointers straight into implementation.

### 2. Prepare the integration branch

Confirm and record the baseline, then create the integration branch. Preserve existing staged and unrelated work; use an isolated worktree when needed. On resume, reconcile the recorded state with the actual branches and tracker before reusing work.

Create a durable **run record** outside the repo and report its path. Update it after reviews, merges, user confirmations, and tracker writes. Keep:

- Baseline and integration commits; each ticket's branch, worktree, status, and blockers.
- Review coverage and finding dispositions; acceptance evidence and the commits it verifies.
- The exact criteria and relevant content the user confirmed.
- Completed and pending tracker operations.
- 任务发现快照及前后差异：查询范围、来源、分页和权限状态，纳入与排除依据，未决关系，依赖图，以及每票的实现、审查、验收和写回状态。入口先保存发现结果，再将其纳入本运行记录。

If the tracker closes work through PRs, or the user asks for one, open a draft PR **after the first merge**, with the appropriate closing references for the spec and tickets. Otherwise the integration branch is the deliverable.

### 3. Implement and review each ready ticket

对尚需实现的每张票分配一个 implementer，使用独立分支和工作树。续接或补发现的票先按 [task-discovery.md](task-discovery.md) 核对已有成果，仅派发缺项。每个 implementer：

1. Confirms its branch is based on the integration branch. Recreate an unused branch from the correct base; preserve existing work before correcting a mistaken base. Never discard work with a hard reset.
2. Calls the Skill tool with `tdd` to build the ticket. Run typechecking and individual test files regularly, and the full suite at the end. Report what ran and what did not.
3. Hands the ticket to the coordinator for a **read-only review subagent**. That reviewer calls the Skill tool with `open-code-review-delegate`, using the ticket context and an explicit diff baseline.
4. Validates the findings, fixes every valid issue, and reruns affected checks. Record reasons for dismissing false positives. Route decisions requiring the user through the coordinator; a missing or failed review tool is a blocker.
5. Merges the integration tip into its branch and verifies affected behavior. Changes introduced by synchronization or conflict resolution receive a follow-up review.
6. Reports commits, review coverage and dispositions, per-criterion evidence, pending human checks, and blockers. Collect evidence here; formal acceptance ticks and closure belong to final acceptance.

A ticket is ready to merge when implementation and review are complete, every valid finding is resolved, affected checks pass, and its branch is synchronized.

### 4. Merge and advance the frontier

Use a **merger subagent** to land tickets one at a time. Recheck the integration tip before each merge; if it advanced, synchronize the ticket again, verify, and review any resulting changes before landing it.

Land each ticket initially as **one Conventional Commit**, using a squash merge when needed. Describe delivered behavior, verification performed and omitted, and reference the ticket with `Refs:`. Preserve implementer branches for recovery and leave existing integration history intact.

Follow the repo's staging and hook rules. If a hook only reformats this run's files, restage those files and retry once. A refusal or second failure blocks the merge; report it without bypassing the hook.

Each successful merge may unlock more tickets: dispatch them immediately. Create the conditional draft PR after the first merge, as described in step 2.

单票阻塞暂停该票及其依赖者，其他已确认独立路径可以继续；任务发现的查询完整性失败则按 task-discovery.md 停止全部实现。保留恢复所需的提交和工作树，报告阻塞；完整交付条件达成前，保持规格未完成、PR 为草稿、待完成票开放。

Proceed when every ticket has landed.

### 5. Review the integration branch

Spawn a read-only subagent to call the Skill tool with `open-code-review-delegate` on the full baseline-to-integration diff, with the spec and all tickets as context.

Use one implementer subagent to validate and fix every valid finding. Record false-positive dispositions and bring user decisions to the coordinator. Rerun affected checks and review the changed portions again.

Land final fixes as separate commits referencing affected tickets. Keep the initial ticket commits intact.

Proceed when the full diff is accounted for under OCR's coverage rules, every valid finding is resolved, and affected checks pass.

### 6. Verify acceptance and write back

现在读取 [acceptance.md](acceptance.md)。先重新发现并对账任务集合，补齐变化影响的工作，再在集成分支逐票复验、批量收集人工确认并写回已获得的验收勾选。

Proceed to handoff only when every ticket has a nonempty acceptance region, every criterion is earned, and write-back has succeeded. Report anything still pending.

### 7. Hand off and clean up

Follow the handoff rules in [acceptance.md](acceptance.md): push before making a draft PR ready or closing tickets directly. Report the branch, PR if present, acceptance results, and actual closure state.

After successful handoff, remove this run's implementer worktrees only after confirming all work is preserved in the integration branch and no unsaved results remain. Keep the integration branch. Report any cleanup failures and remaining paths.
