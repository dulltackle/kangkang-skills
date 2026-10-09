---
name: implement-spec
description: "Implement a spec and its tickets in parallel, with OCR review and verified acceptance criteria."
disable-model-invocation: true
---

# Implement Spec

Implement the entire spec on one **integration branch**, with every ticket resolved the way the issue tracker closes work.

The tickets are a **task graph**, not a list of steps. The **frontier** is the set of tickets whose dependencies have landed and whose requirements are settled. Keep independent ready work running in parallel; reducing token use must not turn the frontier into a default serial queue.

Communicate through **context pointers** to the spec, tickets, research notes, and commits. Keep shared exploration notes outside the repo, accessible to every subagent.

## Which tracker

Read `docs/agents/issue-tracker.md` and the configuration it points to. If none has been provided, tell the user to run `/setup-matt-pocock-skills` before continuing.

## Process

### 1. Read the task graph

Run [task discovery](task-discovery.md) first. Establish query completeness and record the ticket set and relationship evidence, then classify tickets as ready, waiting on dependencies, or blocked. Repeat discovery on resume and at close-out. Incomplete queries stop all implementation; missing dependencies, cycles, and unresolved requirements block affected paths.

Every ticket needs acceptance criteria before implementation. Propose missing criteria for the user's confirmation; only confirmed criteria become the ticket's requirements. Continue independent tickets while that decision is pending.

Optionally use an exploration subagent to investigate code or external documentation and save shared notes. Implementers should be able to follow those pointers straight into implementation.

### 2. Prepare the integration branch

Confirm and record the baseline, then create the integration branch. Preserve existing staged and unrelated work; use an isolated worktree when needed. On resume, reconcile the recorded state with the actual branches and tracker before reusing work.

Create a durable **run record** outside the repo and report its path. Update it after reviews, merges, user confirmations, and tracker writes. Keep:

- Baseline and integration commits; each ticket's branch, worktree, status, and blockers.
- Review coverage: reviewer, baseline and head, files and changes covered, applicable rules, findings and dispositions, and correspondence to the integration diff. Acceptance evidence and the commits it verifies.
- The exact criteria and relevant content the user confirmed.
- Completed and pending tracker operations.
- Discovery snapshots and changes: query scope, sources, pagination and access status, inclusion and exclusion evidence, unresolved relationships, the dependency graph, and each ticket's implementation, review, acceptance, and write-back state. Save discovery results before incorporating them into this record.

If the tracker closes work through PRs, or the user asks for one, open a draft PR **after the first merge**, with the appropriate closing references for the spec and tickets. Otherwise the integration branch is the deliverable.

#### Configuration and continuing authorization

For implementation, resume, and close-out under this skill, make configuration changes required by the confirmed spec or tickets. Before editing, save recoverable originals or exact diffs; record the target, scope of impact, and completion evidence.

On resume, reconcile existing authorization, its scope, and current state. Continue when the target and impact remain materially unchanged. For new costs, broader permissions, unrelated configuration, or discarding user content, complete independent preparation and ask the user to decide. Identify the missing evidence when prior authorization cannot be verified.

Follow host approval requirements. If approval is denied, preserve work and report the denied action and reason; keep the same boundary across paths and tools.

### 3. Implement and review each ready ticket

Use separate branches and worktrees for concurrent implementers. Reuse an available implementer for a compatible ready ticket instead of creating an agent for each lifecycle stage; keep enough implementers active to advance independent work in parallel. Give overlapping edits clear ownership and synchronize their shared changes. For resumed or newly discovered tickets, reconcile existing work through [task discovery](task-discovery.md) and dispatch only missing work. Each implementer:

1. Confirms its branch is based on the integration branch. Recreate an unused branch from the correct base; preserve existing work before correcting a mistaken base. Never discard work with a hard reset.
2. Calls the Skill tool with `tdd` to build the ticket. Runs typechecking, the ticket's acceptance tests, and affected regressions before merge; for changed behavior, identify existing tests of the old interaction before starting expensive checks. Record the tested revision or source identity, scope, environment, results, and omissions. Run the complete project checks at final acceptance rather than automatically per ticket, unless the repository requires them earlier. Development results do not become formal acceptance merely by being reused.
3. Hands the ticket to an independent **read-only review subagent** using `open-code-review-delegate`, ticket context, and explicit baseline and head. Keep the same reviewer for fixes and synchronization of this ticket; give it the new diff and prior findings. Independent tickets may use parallel reviewers. Reviewers must not have implemented the content they assess. If a reviewer becomes unavailable or its context becomes unwieldy, hand off the compact coverage record and source pointers to a replacement.
4. Validates the findings, fixes every valid issue, and reruns affected checks. Record reasons for dismissing false positives. Route decisions requiring the user through the coordinator; a missing or failed review tool is a blocker.
5. Merges the integration tip into its branch and verifies affected behavior. Changes introduced by synchronization or conflict resolution receive a follow-up review.
6. Reports commits, review coverage and dispositions, per-criterion evidence, pending human checks, and blockers. For technical reading criteria, an independent reviewer records each criterion verbatim, the reviewed commit, file locations, and reasoning. Lists items requiring a user decision separately. Collect evidence here; formal acceptance ticks and closure belong to final acceptance.

A ticket is ready to merge when implementation and review are complete, every valid finding is resolved, affected checks pass, and its branch is synchronized.

#### Coordinate by events

While agents or checks run, advance other independent work. Prefer completion or state-change notifications; when nothing is actionable, use the host's blocking wait or suspension within its response constraints. If notifications are unavailable, use bounded queries with backoff, resetting only on meaningful progress or new input. An unchanged status is a reason to wait longer, not to repeat inspection or dispatch replacement work.

Start a long check once and retain its process or job identity and full logs outside the conversation. Read its terminal summary, or bounded failure evidence when needed; use detailed logs to investigate a concrete problem. Agent handoffs carry source pointers, commits, changes, findings, and blockers rather than replaying the conversation. Report meaningful progress and honor required host updates without additional status queries solely to produce an update.

### 4. Merge and advance the frontier

The coordinator lands tickets one at a time, without a dedicated merger agent. Recheck the integration tip before each merge; if it advanced, synchronize the ticket again, verify, and review any resulting changes before landing it.

Land each ticket initially as **one Conventional Commit**, using a squash merge when needed. Describe delivered behavior, verification performed and omitted, and reference the ticket with `Refs:`. Preserve implementer branches for recovery and leave existing integration history intact.

Follow the repo's staging and hook rules. If a hook only reformats this run's files, restage those files and retry once. A refusal or second failure blocks the merge; report it without bypassing the hook.

Each successful merge may unlock more tickets: dispatch them immediately. Create the conditional draft PR after the first merge, as described in step 2.

A blocked ticket pauses that ticket and its dependents; confirmed independent paths may continue. Incomplete discovery queries trigger the global stop in [task discovery](task-discovery.md). Preserve recovery commits and worktrees and report blockers. Keep the spec incomplete, the PR in draft, and unfinished tickets open until all delivery conditions are met.

Proceed when every ticket has landed.

### 5. Review the integration branch

Assign an independent read-only reviewer, reusing a suitable ticket reviewer, to the final integration review. Use OCR's full baseline-to-integration file inventory and current rules to reconcile cumulative ticket-review coverage. For every reviewable entry, record matching prior coverage or perform the missing review; retain OCR's explicit skip reasons and coverage accounting. Reuse prior review only where the reviewed changes, requirements, and applicable rules still match. A file name or earlier “passed” result alone is insufficient.

Focus fresh review on cross-ticket behavior, shared contracts, conflict resolutions, new changes, and coverage gaps. Individually reviewed changes can still interact incorrectly: expand the review wherever their combined behavior is uncertain. Re-read the full diff when coverage cannot be established. Keep per-criterion technical review evidence in addition to OCR coverage.

Return valid findings to the responsible implementer, reusing available agents. Record false-positive dispositions and bring user decisions to the coordinator. Rerun affected checks and have the independent reviewer assess the changed portions again.

Land final fixes as separate commits referencing affected tickets. Keep the initial ticket commits intact.

Proceed when the full diff is accounted for under OCR's coverage rules, every valid finding is resolved, and affected checks pass.

### 6. Verify acceptance and write back

Read [acceptance and handoff](acceptance.md) now. Rediscover and reconcile the ticket set, complete work affected by changes, and match each ticket to valid evidence for the pinned integration commit, running missing or invalidated checks. Check independent technical review evidence, batch only items requiring user decisions, and write back earned acceptance ticks.

Proceed to handoff only when every ticket has a nonempty acceptance region, every criterion is earned, and write-back has succeeded. Report anything still pending.

### 7. Hand off and clean up

Follow the handoff rules in [acceptance.md](acceptance.md): push before making a draft PR ready or closing tickets directly. Report the branch, PR if present, acceptance results, and actual closure state.

After successful handoff, [clean up temporary worktrees](acceptance.md#4-clean-up-temporary-worktrees). On resume, use that procedure to verify ownership of earlier worktrees, continuing cleanup authorization, and recovery evidence. Report what was cleaned up and what remains.
