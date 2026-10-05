# Acceptance and Handoff

Run after integration review and its fixes. The coordinator owns tracker writes and closure; subagents supply evidence.

An `[x]` is a claim backed by execution or explicit user confirmation. Every ticket must have a nonempty acceptance region with every criterion earned before the spec can be handed off.

## 1. Reverify the final state

Re-read each ticket from the tracker. Match evidence to the **exact text** of its current acceptance criteria. Verify added or changed criteria; evidence with no matching criterion pauses that ticket's write-back. Leave unverified criteria unchecked.

On the final integration state, rerun every executable acceptance check, including checks for existing ticks. Run the full suite and typechecking. Record commands, outcomes, and the verified commit in session output and the run record. Earlier worktree results do not replace this verification.

Classify each criterion:

- **`ran`**: executed and observed passing. Earned by that result.
- **`read`**: assessed only by reading. Earned by the user's explicit confirmation.
- **Failed or unverified**: remains unchecked. An executable check that cannot run stays unverified; human confirmation is not a substitute for its execution.

Ask about all `read` criteria in one batch, grouped by ticket. Keep declined or unanswered items unchecked. Retain earlier explicit confirmation only when the relevant content is unchanged.

A failing check loses its existing tick: report the regression and its reason. Reopen a previously closed ticket that has lost acceptance, using the tracker's rules. It can close again only after acceptance is earned again.

Further fixes invalidate affected evidence. Rerun those criteria and the project's final checks on the updated integration state.

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

**With a PR:** push the integration branch, then mark the draft ready for review. Report it as awaiting merge. Let the PR workflow close the spec and tickets. A local tracker with a separate closure field records acceptance now and follows its configured PR workflow for closure.

**Without a PR:** push successfully before closing tickets and the spec through the tracker. Set upstream on the first push as configured. With no remote, state that pushing was skipped and proceed with local closure. A refused push pauses handoff, retaining the branch and open tickets; do not force-push or rewrite history.

**Local closure changes files:** after the acceptance commit is landed and pushed where a remote exists, commit the closure edits separately and push them. If that commit or push fails, report the exact local/remote split, keep recovery materials, and leave handoff incomplete.

A partial failure is not a wholesale rollback. Preserve landed commits and successful remote writes; reverse only this run's uncommitted local ticket edits under the concurrency check above. Before retrying, inspect current state to avoid duplicate comments, duplicate closure, or overwritten edits.
