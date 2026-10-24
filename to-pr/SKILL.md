---
name: to-pr
description: "Deliver the current branch as a pull request that closes its tickets on merge: draft until every acceptance criterion is earned, ready once it is. Use when the user wants to open or update a PR for ticket work, or at the end of /implement and /implement-spec. Safe to re-run."
---

# To PR

Put the current branch on the remote as **one PR for its tickets**. The body says `Closes #<n>` from the start; **draft status is the gate**, since a draft cannot merge. The ticket closes when the PR merges, and no step of this skill closes or reopens a ticket.

Read state from git, the PR, and the tracker, never from another skill's memory. Whoever committed the work (/implement, implementer subagents, or the user by hand), this skill does the same thing.

Re-running is normal: a PR that already exists for the branch is updated, never duplicated.

## Process

### 1. Identify the tickets

Read `docs/agents/issue-tracker.md` for how to read tickets. If it is missing, tell the user to run `/setup-matt-pocock-skills`.

Find `<default>` with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`, then `git fetch origin` so `origin/<default>` and the remote branches are current.

Take the first source that names any ticket:

1. The user's arguments.
2. The `Closes #<n>` lines in the body of the branch's existing PR (`gh pr view --json body`). A detached `HEAD` has no PR.
3. The `Refs: #<n>` trailers of the commits on `origin/<default>..HEAD`.

None found → stop and ask which ticket this delivers.

### 2. Check the tree

Stop and report, changing nothing, when:

- there is no remote: a PR needs one;
- the tree has staged or unstaged changes: commit them first;
- `HEAD` has no commits ahead of `origin/<default>`: there is nothing to deliver.

### 3. Get onto a feature branch

- **A feature branch** → use it.
- **Detached `HEAD`** → `git switch -c issue-<n>`, `<n>` being the first ticket.
- **The default branch** → `git switch -c issue-<n>` the same way, and report that local `<default>` is now ahead of the remote by those commits. Never reset it: moving the user's branch back is their call.

If `issue-<n>` already exists, locally or on the remote, at another commit → stop and report. Never overwrite a branch.

### 4. Verify the tickets

Read the default branch's **required checks**, the merge gate:

```bash
gh api repos/{owner}/{repo}/branches/<default>/protection/required_status_checks --jq '.contexts'
gh api repos/{owner}/{repo}/rules/branches/<default>   # rulesets: type "required_status_checks"
```

An unticked criterion is **merge-gated** when its text asks for exactly this: this PR passing some or all of those required checks. GitHub enforces it before merge, so it need not be earned first. Unreadable protection or no required checks → nothing is merge-gated.

Re-read every ticket from the tracker. A ticket is a **parent** when another ticket in the set belongs to it, the way `docs/agents/issue-tracker.md` records that (on GitHub: a sub-issue, or a child naming it in `Part of #<n>` or a `## Parent` section). A spec delivered with its tickets is the usual parent, and it usually has no region of its own.

For every ticket with a region, parents included when they have one, call the Skill tool with "verify-acceptance" and run all of its steps against `HEAD`. Do this on every run, ticked or not: it re-runs every executable criterion, `[x]` ones included, so a box that stopped being true loses its tick before the PR can merge. Merge-gated criteria stay `[ ]` for the gate to settle. On a local tracker, commit its ticket edits as a follow-up `chore:` commit before pushing.

When any criterion fails on `HEAD` (a run that failed, or a regression that lost its tick), stop before pushing: failing work stays local. If the branch already has a PR that is ready, mark it back to draft first (`gh pr ready <pr> --undo`) so it cannot merge, then report. Leave the PR body as it is: the ticket and its comment carry the regression.

### 5. Decide draft or ready

A ticket is **ready** when its region is non-empty and every box in it is `[x]` or merge-gated. A parent is ready when every child in the set is, and every box in its own region, if it has one, is `[x]` or merge-gated. The PR is **ready** when every ticket is; otherwise it is a **draft**. A non-parent with no region, an unverified criterion, one awaiting the user's word: all draft.

### 6. Write the body

- **No PR yet** → call the Skill tool with "pr" for the body, then append the ticket section from the template below.
- **The branch has a PR** → keep its body and replace only the ticket section. Do not call "pr" again: the body already says what the change is.

Keep the ticket section short: the PR is a pointer to the tickets, not a copy of them.

### 7. Push

`git push -u origin <branch>` the first time, `git push` after.

**A refused push** (non-fast-forward, protected branch, pre-push hook) stops the run. Report it and hand back the command to retry. `pull --rebase` rewrites the user's commits and `--force` is off the table: the remote is the user's gate, exactly as a pre-commit hook is.

### 8. Open or update the PR

```bash
gh pr view --json number,url,isDraft          # does the branch have one?
gh pr create --base <default> --title "<title>" --body-file "$TMPDIR/pr-body.md" [--draft]
gh pr edit <pr> --body-file "$TMPDIR/pr-body.md"
gh pr ready <pr>             # draft → ready
gh pr ready <pr> --undo      # ready → draft, when a criterion lost its tick
```

Title: the commit subject when there is one commit, otherwise the ticket's title. An existing PR keeps its title.

For another tracker or forge, take the equivalent commands from `docs/agents/issue-tracker.md`; where it gives none, stop and ask.

Do not wait for CI and do not merge. Merging is the user's decision.

### 9. Report

```
PR #57 (draft) https://github.com/o/r/pull/57 ← branch issue-42, pushed
#42 open: concurrent writes lose no orders (not verified)
#43 ready: acceptance 4/4 ticked
Guaranteed by the merge gate: PR passes check
```

A run that stopped says where and why instead of the PR line:

```
⚠ #46 "export keeps column order" fails on HEAD (export.test.ts), unticked
Stopped before pushing: PR #71 marked back to draft, body unchanged
```

One line per ticket, in the ticket section's wording. Add any line from step 3, such as `local main is 2 commits ahead of the remote, not reset`. When an open criterion waits on the PR's own CI and nothing is merge-gated, add `re-run to-pr once CI has finished`.

## Template

Write the ticket section and the report in the language the user's instructions or the repo's history use. The template fixes the structure, not the language. `Closes` is GitHub's keyword, so it stays as it is.

<ticket-section>
## Tickets

Closes #42

- #42: acceptance 3/4 ticked. Open: concurrent writes lose no orders (not verified)
- Guaranteed by the merge gate: PR passes check, process-trace
</ticket-section>

- One `Closes` line per ticket.
- Per ticket, one line: ticks earned, then what is still open and why.
  - every box ticked: `acceptance 4/4 ticked`
  - only merge-gated boxes open: `acceptance 5/6 ticked, the remaining 1 guaranteed by the merge gate`
  - a criterion the user declined: `Open: README updated (declined by the user)`
  - no region: `no acceptance region`
  - a parent: `ready: children #11, #12 are ready` or `waiting on children: #21`, plus its own ticks if it has a region
- Drop the merge-gate line when nothing is merge-gated.
