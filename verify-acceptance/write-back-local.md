# Write-back: local markdown tracker

For repos whose `docs/agents/issue-tracker.md` configures **local markdown**. One file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.

The ticket file is *in* the repo, so every edit to it lands in a commit. Edit it with the Edit tool; the caller commits it on top of the work it verifies.

## The acceptance-criteria region

The local ticket template gives the criteria no heading, so shape delimits the region:

- **It starts** at the first checkbox below the `**Status:**` line.
- **It ends** at the first line that is neither a checkbox nor blank: prose, a heading, anything.
- **Nested checkboxes** neither end the region nor get ticked. Step past them.

```markdown
**Status:** ready-for-agent

- [ ] Criterion 1      ← region starts
  - [ ] Sub-item       ← skipped, region continues
- [ ] Criterion 2      ← region ends here

Scratch notes:         ← terminator
- [ ] Hand-written todo  ← outside; never touched
```

This cuts the region short rather than long on purpose. A stray line between criteria costs a tick you then report as unverified; the other way round silently ticks somebody's todo list. A lost tick is visible, so when in doubt, don't tick.

## The comment

Append it under a `## Comments` heading at the bottom of the file, per the local conventions in `docs/agents/issue-tracker.md`. **The ticket template does not create that heading**: on a ticket's first write-back it will not be there, so add it at the end of the file, then append under it.

Drop the sha from the comment's first line and keep the branch: the file lands *in* that commit, so `git log --follow` recovers it.

The `**Status:**` line stays as it is: this skill never closes or reopens a ticket.

## Rolling back

Whenever a run stops before its ticket edit is committed (a mismatch, a write failure, a hook refusing that commit), the ticks already written come back off:

```bash
git checkout -- .scratch/<feature-slug>/issues/<NN>-<slug>.md
```

**The path is mandatory and it is one file.** `git checkout .`, `-- .`, `git restore .` and `-A` are all forbidden here: widening this command past the single ticket file destroys the session's entire work, the exact work sitting uncommitted in the tree at the moment you run it.

```
⚠ #03 write-back failed: the ticket has "concurrent writes lose no orders", but nothing verified this run matches it.
  Nothing changed, nothing committed. The tree is as it was; check the ticket and re-run.
```

**Rollback only reaches a tracked file.** On a ticket's first run the file is usually untracked, since ticket files are written but not committed until the first write-back is, and `git checkout` fails with `pathspec did not match`. That is expected: leave the edits in place and say plainly what was written, so the user can undo it by hand.

```
⚠ #03 not committed. The ticket file is not under version control, so it cannot be rolled back.
  Written: ticked 2 acceptance criteria. Check them by hand and re-run.
```

## Committing the edit

Each write-back pass lands as its own follow-up `chore:` commit on top of the work it verifies; never amend. Once one has landed, a failure in a later pass (the confirmation pass) is a split state, not a rollback: name the criteria the ticket is behind by.
