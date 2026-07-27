---
name: to-commit
description: Commit a completed ticket as one Conventional-Commit, verifying each acceptance criterion, then checking it off on the ticket itself and closing the ticket. Invoked by /implement at the end of a ticket session.
---

# To Commit

Commit the current session's work as **one commit for the ticket** being implemented,
then record the verified acceptance criteria back onto the ticket.

The issue tracker should have been provided to you — run /setup-matt-pocock-skills if not.
Read `docs/agents/issue-tracker.md` first: steps 5 and 7 write back to the tracker, and
which commands to use depends on which tracker this repo configured.

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

5. **Check off the verified criteria on the ticket.** Flip only the boxes step 3
   actually verified — never check a box you did not exercise, and leave unmet
   ones `[ ]`. **When** this happens depends on the tracker:

   - **Local markdown** — the ticket is a file in the repo, so edit it *before*
     committing and stage it alongside the code; the checkbox change belongs in
     the same commit as the work that earned it.
   - **GitHub / GitLab** — the ticket lives off-repo, so defer the write-back to
     step 7, once the commit has landed. Never flip a box on a remote ticket for
     a commit that failed to be created.

   See "Write-back by tracker" below for the commands.

6. **Compose the message** from the template and commit to the current branch.
   Never use a closing keyword (`Closes`/`Fixes`): it only fires when the commit
   reaches the default branch, and this skill does not push — relying on it would
   leave the ticket open indefinitely. Step 7 closes the ticket explicitly instead.

7. **Close the ticket** — only when *every* acceptance criterion is `[x]`. If any
   criterion is unmet, still do the step-5 write-back but leave the ticket open,
   and tell the user which criteria are holding it open. For GitHub/GitLab this is
   also where the step-5 checkbox write-back happens.

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
- **Local-markdown tracker:** there are no issue ids — use `Refs: <path to the ticket
  file>`, e.g. `Refs: .scratch/<feature-slug>/issues/03-<slug>.md`.

## Write-back by tracker

The checklist in the commit message is a snapshot; the ticket is the source of truth.
Both carry the same marks.

**GitHub.** Read the current body, flip the verified boxes, write it back, then close:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file: - [ ] <criterion>  →  - [x] <criterion>
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue close <n> --comment "All acceptance criteria verified in <short-sha>."
```

Edit the body by matching each criterion's text. Never regenerate the body from the
commit message — that would drop everything else the ticket carries.

**GitLab.** Same shape with `glab`; `glab issue close` takes no comment, so post the
note first:

```bash
glab issue view <n> -F json | jq -r .description > "$TMPDIR/issue-<n>.md"
# edit that file: - [ ] <criterion>  →  - [x] <criterion>
glab issue update <n> --description "$(cat "$TMPDIR/issue-<n>.md")"
glab issue note <n> --message "All acceptance criteria verified in <short-sha>."
glab issue close <n>
```

**Local markdown.** One file per ticket under
`.scratch/<feature-slug>/issues/<NN>-<slug>.md`. Edit the checkboxes in place with the
Edit tool, set the `Status:` line near the top to the repo's completed state (`Status:
done` unless the repo's existing issue files use another word), and stage the file with
the code so both land in the step-6 commit.

Because that file is part of the commit, edit it *before* `git commit`. If the commit
has already been made, do not amend — land the ticket edit as a follow-up `chore:`
commit and say so.
