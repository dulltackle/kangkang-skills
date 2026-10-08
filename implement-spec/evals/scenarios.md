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
