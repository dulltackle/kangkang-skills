---
name: to-commit
description: Commit a completed ticket as one Conventional-Commit, verifying each acceptance criterion before checking it off. Invoked by /implement at the end of a ticket session.
---

Commit the current session's work as **one commit for the ticket** being implemented.

The issue tracker should have been provided to you — run /setup-matt-pocock-skills if not.

## Process

1. **Identify the ticket.** It is usually already in context from /implement. If not, ask.

2. **Peek at house style.** Read the repo's recent `git log` for an established
   convention — scope vocabulary, tense, casing. Local convention outranks the
   template below; the template is the fallback when no convention exists.

3. **Gate on the acceptance criteria.** Walk the ticket's acceptance criteria
   one by one and *verify* each against the work — run the relevant tests,
   exercise the behavior. A criterion is checked `[x]` only when verified.
   If any criterion is unmet, stop and surface it to the user: committing
   with unmet criteria requires their explicit say-so, and the checklist
   shows `[ ]` for anything unmet (with a one-line reason).

4. **Split out prefactoring.** If the session prefactored before building
   (“make the change easy, then make the easy change”), land that as its own
   `refactor(...)` commit first. This is the only exception to
   one-commit-per-ticket.

5. **Compose the message** from the template and commit to the current branch.
   Never use a closing keyword (`Closes`/`Fixes`) — closing belongs to /to-pr.

<commit-template>

<type>(<scope>): <imperative summary derived from the ticket title>

<one or two lines: the end-to-end behavior this commit delivers, from the
ticket's "What to build">

Acceptance criteria:
- [x] <criterion, verified>
- [ ] <criterion, unmet — committed with user sign-off: reason>

Refs: #<ticket id>

</commit-template>

Template notes:
- `type` reflects the nature of the slice (`feat`, `fix`, `refactor`, …).
- `scope` only if the repo's log shows an established scope vocabulary; otherwise omit.
- **Local-markdown tracker:** there are no issue ids — use `Refs: <ticket title>`
  exactly as it appears in tickets.md so /to-pr can match it. Do not edit
  tickets.md; marking tickets done belongs to /to-pr.
