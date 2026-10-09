# Acceptance and handoff

Run after integration review and its fixes. The coordinator owns tracker writes and closure; subagents supply evidence.

Every acceptance tick requires matching execution results, independent technical review evidence, or explicit user confirmation, classified below. Every ticket must have a nonempty acceptance region with every criterion earned before the spec can be handed off.

## 1. Verify the final state

Run [task discovery](task-discovery.md) to rediscover the complete ticket set and reconcile it with the run record. Apply its global stop for incomplete queries and its recovery procedure for added, missed, or changed relationships. Complete affected implementation and review before returning to acceptance. Track commits, review, acceptance evidence, and write-back state against each ticket's current criteria; parent acceptance, apparent code coverage, and closed status cannot replace child-ticket evidence.

Re-read each ticket from the tracker. Match evidence to the **exact text** of its current acceptance criteria. Verify added or changed criteria; evidence with no matching criterion pauses that ticket's write-back. Leave unverified criteria unchecked.

After final integration review and fixes, pin the integration commit. Every executable criterion, including existing ticks, the full test suite, typechecking, and required project checks need valid evidence for that commit. Prefer the project's established formal acceptance entry point; otherwise use a separate checkout of the pinned commit with locked dependencies. Record the commit, source identity, commands and scope, environment, results, and log locations.

Reuse an earlier passing formal run when it verifies this exact commit, current criteria and check scope, and the same relevant environment; run only missing or invalidated checks. Moving from merge to acceptance or handoff does not itself invalidate evidence. An ordinary development-worktree result, identical start/end fingerprints, a skipped or failed check, or evidence for another commit does not qualify. Preserve repository-specific requirements and freshness windows: actual-host or deployment checks must still verify the delivered instance and build within their validity period.

Classify each criterion:

- **`ran`**: an executable requirement was run and observed to pass. Record the tested commit, command, result, and environment gaps. Unrun, failed, or skipped requirements remain unaccepted; review and user confirmation cannot replace execution.
- **`reviewed`**: a clear technical requirement can be assessed by reading source or documentation. A reviewer who did not implement that content verifies it, recording the criterion verbatim, reviewed commit, file locations, reasoning, reviewer identity, and unresolved issues. The coordinator checks that correspondence before ticking. A generic OCR pass or implementer assertion is insufficient. Prefer deterministic checks for mechanically decidable requirements and record their results as `ran`.
- **`user`**: product tradeoffs, subjective experience, added scope, ambiguous or conflicting criteria, and criteria explicitly requiring user confirmation need the user's decision or acceptance. Preserve explicit confirmation requirements when classifying. Execute any runnable part as well.
- **Failed, unverified, or incomplete evidence**: leave unchecked. Reconcile legacy `read` entries with current criteria and content, then obtain independent review evidence or valid user confirmation before acceptance; `read` does not automatically become `reviewed`.

Batch only `user` items into one request, grouped by ticket. Leave declined or unanswered items unchecked. Reuse explicit confirmations only while relevant content remains unchanged. Ask for clarification when technical review finds ambiguous criteria; preserve the acceptance bar. A skill update alone does not retroactively change earlier tickets' acceptance or closure state.

A failing check loses its existing tick: report the regression and its reason. Reopen a previously closed ticket that has lost acceptance, using the tracker's rules. It can close again only after acceptance is earned again.

Later code fixes require affected regressions and complete formal project checks for the new integration commit; have an independent reviewer reassess changed reading criteria. Reuse a qualifying run already performed on that new commit rather than running it again at handoff. Changes to relevant dependencies, configuration, environment, criteria, or check scope also require renewed matching evidence. Tracker-only remote writes do not change the tested commit. Local acceptance or closure commits must follow the repository's evidence policy; absent an explicit rule allowing record-only commits, formally verify the new delivery commit. Reconcile evidence with the delivery target before handoff.

## 2. Write earned acceptance back

Re-read immediately before each write. Change only exact-matched checkboxes inside the acceptance region; preserve other lists and prose. Use conditional writes when supported. On concurrent edits, reconcile against the fresh body rather than overwriting it with a stale copy.

Append a concise record of commits and branch, executed checks, user confirmations, revoked ticks, and outstanding items. Keep full command evidence in session output and the run record. Follow the repository's language conventions for comments and commit messages.

Verified items may be written while human confirmation is pending; handoff still requires every criterion to be earned.

### External tracker

Commit code and fixes before write-back. If either the body update or comment fails, pause further writes and handoff. Report completed and pending operations; retain landed commits and successful remote writes. On resume, inspect the current state and complete only missing operations.

### Local Markdown tracker

Put acceptance edits and required logs in a separate Conventional Commit, preserving the initial code commits.

Save the affected acceptance and log fragments before editing. If the commit fails, revert only this run's uncommitted write-back. First compare each current fragment with the version this run wrote: reverse it only if they still match. If somebody changed it, preserve the current content and report the conflict.

Preserve the user's staging set. Unrelated staged changes block this close-out commit until resolved; neither include nor unstage them. A formatting-only hook allows one restage-and-retry of this run's files. A refusal leaves the code commits intact and is reported.

## 3. Push and hand off

Start when every ticket is all green, write-back succeeded, and the final work is committed.

Before handoff actions, repeat [task discovery](task-discovery.md) to confirm the ticket set and relationships, and read current acceptance criteria and write-back state. Reconcile changes and repeat affected acceptance. Mark a PR ready, close work directly, or claim full delivery only when every ticket in the latest complete set and the parent spec meet their own acceptance, review, and write-back conditions. Record actual closure state; tickets awaiting PR merge remain open.

**With a PR:** push the integration branch, then mark the draft ready for review. Report it as awaiting merge. Let the PR workflow close the spec and tickets. A local tracker with a separate closure field records acceptance now and follows its configured PR workflow for closure.

**Without a PR:** push successfully before closing tickets and the spec through the tracker. Set upstream on the first push as configured. With no remote, state that pushing was skipped and proceed with local closure. A refused push pauses handoff, retaining the branch and open tickets; do not force-push or rewrite history.

**Local closure changes files:** after the acceptance commit is landed and pushed where a remote exists, commit the closure edits separately and push them. If that commit or push fails, report the exact local/remote split, keep recovery materials, and leave handoff incomplete.

A partial failure is not a wholesale rollback. Preserve landed commits and successful remote writes; reverse only this run's uncommitted local ticket edits under the concurrency check above. Before retrying, inspect current state to avoid duplicate comments, duplicate closure, or overwritten edits.

## 4. Clean up temporary worktrees

This procedure applies to close-out and resume under `implement-spec`.

After successful handoff, clean up temporary worktrees owned by this run by default. On resume, include earlier worktrees whose ownership is established by reliable run records. Record each path, creation ownership, and recovery evidence. Preserve primary checkouts, shared or unrelated worktrees, and those the management tool marks ineligible for cleanup.

Before cleanup, verify that work is integrated or recoverable from verified commits or backups. Inspect staged, unstaged, untracked, and ignored files. Preserve and verify recovery of concrete signs of unsaved content. If cleanup requires discarding content or ownership is unclear, pause that worktree and ask the user to decide. The absence of an editor-buffer API alone is not a blocker.

Once these conditions hold, proceed without asking for cleanup authorization again. Use the management interface that created the worktree, or normal removal for ordinary Git worktrees. Preserve the integration branch and implementation branches or backups needed for recovery.

If permissions, active use, or host approval block cleanup, retain that worktree and its recovery evidence, record the reason and remaining path, and continue with other eligible worktrees. Completed handoff remains valid; report cleanup separately. Respect removal and approval boundaries without forced deletion or hard resets.
