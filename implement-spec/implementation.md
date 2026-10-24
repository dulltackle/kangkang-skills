# Implementation, review, and merging

## Implement ready tickets

Give concurrent implementers separate branches and worktrees based on integration. Reuse available implementers for compatible tickets and assign ownership of overlapping edits explicitly. Reconcile existing work before resuming or adding tickets; complete only missing work. Recreate an unused branch with the wrong baseline if needed; preserve existing work and history first.

Include the entry point's conditions for reporting stalls in each assignment. Implementers promptly report to the coordinator, who informs the user.

1. Use TDD at the agreed highest observable seam. Find existing interaction tests before changing behavior. Run typechecking, ticket acceptance tests, and affected regressions; record source identity or commit, scope, environment, results, and omissions. Run full project checks on the final stable candidate by default, subject to stricter repository rules.
2. Give an independent read-only `open-code-review-delegate` reviewer the ticket context and explicit baseline and target. The reviewer must be independent of that content's implementation. Keep the same reviewer through the ticket's fix loop, passing new diffs and findings together. If the reviewer is unavailable or its context is exhausted, hand off compact coverage records and source pointers. Missing or failed review tools block review.
3. Validate findings, fix valid issues, record false-positive reasoning, and rerun affected checks. Refer user tradeoffs to the coordinator. Verify interactions after synchronizing with integration; review diffs introduced by synchronization or conflict resolution.
4. Report the commit, review coverage and dispositions, per-criterion evidence, and blockers. Technical reading evidence includes the exact criterion, commit, file locations, and independent reviewer's reasoning. Record user tradeoffs separately. Collect evidence here; perform formal acceptance write-back at the end.

Merge only after implementation, review, valid-finding fixes, targeted checks, and synchronization are complete.

## Coordinate and advance

Keep independent work moving in parallel and advance other ready work while waiting. Prefer completion and state-change notifications; otherwise use bounded status queries with backoff. Increase waits when state is unchanged. Preserve running agents and checks rather than creating replacements to poll them. Start each long check once and save its original session or job identity and full logs. Read the terminal summary, then failure details as needed. Hand off source paths and compact state instead of replaying history; maintain host-required progress updates.

The coordinator merges sequentially, without a dedicated merger. Check the integration tip before each merge; if it has advanced, synchronize again, validate, and review the resulting changes. Land one initial Conventional Commit per ticket, squashing when needed, describing behavior, verified and unverified work, and `Refs`. Preserve implementation branches and original integration history. A formatting hook permits one restage-and-retry of this run's files; respect a refusing hook.

Advance the newly ready frontier immediately after each merge. Open the draft PR after the first merge, as [run records](run-record.md) describe. A ticket blocker affects that ticket and its dependents. For query failures, follow [failure and recovery](task-discovery.md#failure-and-recovery): pause new dispatch, integration, and write-back while permitting eligible preassigned local work. Preserve recovery materials and unfinished tickets. Once every ticket has landed, enter integration review.
