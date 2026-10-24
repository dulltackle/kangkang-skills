---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, spawn one read-only subagent with the ticket context that calls the Skill tool with "open-code-review-delegate" to review the work. If the `ocr` CLI is missing, stop and report that review is blocked. Validate its findings, fix the valid ones, and rerun the affected tests.

Commit your work to the current branch, first running `git switch -c issue-<n>` (`<n>` being the ticket) when that is the default branch or a detached `HEAD`. Then call the Skill tool with "to-pr", passing the ticket reference, to deliver it as a pull request.
