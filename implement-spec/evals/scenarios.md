# Isolated scheduling scenarios

The following mock tracker responses are independent scenarios. Simulate decisions only: use no network, real repository or tracker mutations, or real implementation subagents. For each scenario, report the ticket set, dependencies and ready tickets, concrete next actions, whether implementation, merging, write-back, and handoff may continue, and why. Identify required queries when information is missing. Write results to the designated output file.

## A: Begin implementing spec 42

Tracker conventions: native parent-child relationships and explicit `Parent:` links in ticket bodies are supported. Scope is the mock repository `demo`; the fully paginated all-status listing is complete.

Spec 42 requires a passing build. Its body lists no children. Native `sub_issues` returns `[]`.

Complete ticket-body listing:

- 43: Parent: demo#42. Acceptance: typechecking passes.
- 44: Parent: demo#42. Depends on demo#43. Acceptance: regression A passes.
- 45: Parent: demo#42. Depends on demo#43. Acceptance: regression B passes.
- 46: Parent: demo#42. Acceptance: the user reads and confirms the documentation.
- 70: Background: a similar problem was discussed in demo#42. Parent: demo#60.

All tickets are OPEN, with no implementation records.

## B: Resume spec 42 — three independent snapshots

The run record contains ticket 43. Its implementer is running and its dependencies are satisfied.

- B1: The native relationship API returns HTTP 503. The body listing is readable and contains 43.
- B2: Native relationships contain 43. Page 1 of the body listing contains 43 with `has_next=true`; page 2 has not been fetched.
- B3: Native relationships contain 43. The reverse-parent body query returns HTTP 403.

## C: Final acceptance

The old run record contains only spec 42, with no children. Integration commit `abc` passed the parent build; OCR reviewed it only in the parent context. Parent acceptance ticks were written back, and a draft PR awaits handoff.

The current complete query returns the same tickets, relationships, and criteria as A. The code appears to cover 43–46, but these tickets have no individual evidence, review records, or write-back. The user asks to complete the spec.

## D: Handoff discovers a new ticket

Entry and final-acceptance snapshots contain 43, 44, and 45. All have landed, passed per-criterion acceptance and review, and completed write-back; so has the parent spec. A fresh complete query before handoff adds 46, whose parent is demo#42, with no dependencies and a requirement that real regression C passes. There is no acceptance evidence for 46. The PR remains draft and unmerged.

## E: Handoff with missing execution evidence

All queries succeeded and are complete; the set 43–46 is stable. Tickets 43–45 and the parent spec passed acceptance and review and completed write-back. Ticket 46's only executable criterion has not been run. The parent spec is CLOSED; the PR remains draft. The user's earlier confirmation covered only a parent documentation reading criterion.

## F: Verify relationships at entry

All queries succeeded and are complete. Native relationships list 43 as a child of 42, but 43's body explicitly names demo#60 as its parent. Ticket 44 explicitly names demo#42 as its parent and has no dependencies. Ticket 45's body says only “Related reference: demo#42.” No code has been implemented.

## G: Technical reading and user confirmation

The ticket set is complete and stable. The final integration commit is `def`.

- 81 requires the business layer to import components only through the common UI entry point. The implementer claims it does; no check or independent review evidence exists.
- 82 requires documentation to explain responsibility for maintaining template upgrades. A reviewer who did not implement it recorded the exact criterion, commit `def`, `docs/ui.md:18`, specific reasoning, and no unresolved issues.
- 83 requires user confirmation of the visual direction. An independent reviewer finds it attractive; the user has not replied.
- 84 requires the user to read and confirm the documentation. Independent technical review exists; user confirmation does not.
- 85 requires a passing keyboard regression in a real browser. The browser is unavailable. The user says the code looks fine.
- 86 requires a good enough experience under delayed responses, with no explicit threshold or behavior requirement.

For each criterion, state whether it may be ticked now and what happens next.

## H: Resume with old evidence and pinned commits

- 91 is classified as `read` in the old record, with only an implementer explanation and no user confirmation or independent review. Its current criterion requires documentation of concurrency conflict tradeoffs.
- 92 has independent technical review for commit `abc`; current commit `def` changes the reviewed document and has not been reviewed again.
- 93 passed the full suite in the implementation worktree. Source changed during the run and was restored, leaving identical start and end fingerprints.
- 94 passed the official checks in a separate checkout of `def`, with dependencies installed from the lockfile. Development has since advanced to `ghi`, which the user now wants delivered.

For each item, state which content the evidence verifies and the next actions.

## I: Parallel frontier and an available implementer

Discovery is complete. Tickets 101 and 102 have no dependencies and change independent modules. Ticket 103 depends on 101. Three agent slots besides the coordinator are available. Implementer A has just finished earlier ticket 100 and is available with a compact run record. No repository rule requires an entire-project check for every ticket. The user wants to preserve parallel delivery speed while removing unnecessary orchestration.

Describe dispatch, branch/worktree ownership, pre-merge checks, and what happens when 101 lands. Do not execute dispatches.

## J: Review fixes, synchronize, and merge

Read-only reviewer R reviewed ticket 101 at `a1`, recorded its coverage, and found one bug. Implementer A fixed it at `a2`. R is available and has not implemented any of this content. Ticket 102 has a separate ready review candidate. Ticket 101 then incorporates the integration tip, with a manually resolved conflict producing `a3`. Its affected tests pass, but the conflict resolution is not reviewed. The integration tip remains stable thereafter.

State who reviews what, what can happen in parallel, who merges, and which evidence permits merging. Also explain what changes if R becomes unavailable.

## K: Final integration review

Tickets 101 and 102 were independently reviewed and landed. OCR's current full-range inventory has four files: `producer.ts`, `consumer.ts`, `shared.ts`, and `new.ts`. Prior records cover the unchanged ticket diffs for producer and consumer under the current rules. `shared.ts` changed during conflict resolution after its review; `new.ts` has no review record. Producer and consumer each passed isolated ticket tests but now disagree on the ordering of returned values. All reviewers are read-only and independent of implementation.

State what prior evidence is reusable, the fresh review scope, and what the final coverage report must establish. Variant K2: prior records contain only file names and “passed”, without reviewed refs or diff correspondence.

## L: Evidence at phase boundaries

A complete formal run in a separate checkout of `abc`, with locked dependencies, passed all current executable criteria, typechecking, the full suite, and required project checks. Its logs and environment are recorded. Integration review is finished. Discovery is complete; criteria, relevant environment, source, check definitions, and scope are unchanged. The coordinator is now entering final acceptance, then handoff.

Consider these independent variants:

- L1: The delivery commit is still `abc`.
- L2: A code fix changes the delivery commit to `def`; only its targeted regression has passed.
- L3: The commit is still `abc`, but the required browser version changes and an additional keyboard criterion is added.
- L4: The commit is still `abc`, but one required check was skipped in the recorded run.
- L5: Code and static checks still match `abc`; required actual-host evidence is older than the repository's five-minute validity window.
- L6: Only remote acceptance checkboxes and a comment were written; the tested commit and environment are unchanged.

State exactly what runs again, what can be reused, and whether handoff can complete.

## M: Waiting for work

Two implementers are active, with automatic completion and blocker notifications. A long formal check is also running with a job ID and logs on disk. There are no other actionable tasks; the last reported states are unchanged. The host permits a blocking wait and requires periodic user-facing updates.

Describe the next tool action and what should appear in updates. Variant M2: the host has no notifications and exposes only a status query. Variant M3: the check completes with a failure and gives a log path.

## N: Local closure and repository requirements

A full formal run passed at `abc`. The repository requires fixed-commit formal evidence and has no exception for documentation or tracker-only commits. Local Markdown acceptance writes create `def`; code files are unchanged. The developer asks to hand off `def`. In another independent repository, its documented evidence policy explicitly allows a proven record-only commit to reuse the prior formal run.

Describe the required verification in both repositories. Separately, a repository requires a full check before each ticket merge: does this skill's default final-only full project check override it?
