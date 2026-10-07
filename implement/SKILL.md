---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, spawn one read-only subagent with the ticket context to run /open-code-review-delegate. Validate and fix its findings, rerun affected tests.

Use /to-commit to commit your work to the current branch.
