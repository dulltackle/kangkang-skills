# Write-back — local markdown tracker

For repos whose `docs/agents/issue-tracker.md` configures **local markdown**. One file per ticket
under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.

The ticket file is *in* the repo, so the tick and the work that earned it belong in the same
commit. **Edit the file with the Edit tool before `git commit`** and stage it with the code.

## The acceptance-criteria region

`/to-tickets`' local template gives the criteria no heading, so the region has to be delimited by
shape instead:

- **It starts** at the first checkbox below the `**Status:**` line.
- **It ends** at the first line that is neither a checkbox nor blank. Any prose, any heading,
  anything else — the region is over.
- **Nested checkboxes** neither end the region nor get ticked. Step past them; never descend.

```markdown
**Status:** ready-for-agent

- [ ] 标准 1          ← region starts
  - [ ] 子项           ← skipped, region continues
- [ ] 标准 2          ← region ends here

随手记的备忘：       ← terminator
- [ ] 手写 todo       ← outside; never touched
```

This cuts the region short rather than long on purpose. A stray line between criteria costs you a
tick you then report as unverified; the other way round silently ticks somebody's todo list. Losing
a tick is visible, and the standing rule is when in doubt, don't tick.

## The comment

Append it under a `## Comments` heading at the bottom of the file, per the local conventions in
`docs/agents/issue-tracker.md`. **The template does not create that heading** — on a ticket's first
write-back it will not be there. Add it at the end of the file, then append under it.

Leave the `**Status:**` line untouched. Ticket status is the user's to change.

## Rolling back

**Whenever a local run stops before its commit lands** — a pre-commit hook refusing, a mismatch, a
write failure, anything at all — the ticks already written have to come back off. Otherwise the
ticket sits there ticked for a commit that will never exist. An unearned `[x]` outliving the run is
the one failure this skill exists to prevent.

```bash
git checkout -- .scratch/<feature-slug>/issues/<NN>-<slug>.md
```

**The path is mandatory and it is one file.** Never `git checkout .`, never `-- .`, never
`git restore .`, never `-A`. Widening this command past the single ticket file destroys the entire
session's work — the exact work that is sitting uncommitted in the tree at the moment you run it.

Abandoning the run here costs nothing else: the working tree still holds everything /implement
produced, so the user fixes the cause and re-runs.

```
⚠ #03 写回失败：ticket 上有「并发写入不丢单」，但本轮未验证到对应项。
  未做任何修改，未提交。工作树原样保留，请确认 ticket 后重跑 /to-commit。
```

**Rollback only reaches a tracked file.** On a ticket's first run the file is usually untracked —
`/to-tickets` writes ticket files but never commits them, so nothing gets tracked until this
skill's own first commit. `git checkout` then fails with `pathspec did not match`. That is
expected, not an error to work around: leave the edits in place and say plainly what was written,
so the user can undo it by hand.

```
⚠ #03 未提交。ticket 文件尚未纳入版本控制，无法回滚。
  已写入：勾选了 2 条验收标准。请手动确认后重跑。
```

## Template variations

- **Commit message** — no issue ids. Use `Refs: .scratch/<feature-slug>/issues/<NN>-<slug>.md`.
- **Comment** — drop the sha from the first line and keep the branch. The file is *in* that commit,
  so `git log --follow` recovers it.

## The second pass

By the time the second write-back runs, the commit has already landed and it carries the
first-pass ticks. **Do not amend it.** Land the ticket edit as a follow-up `chore:` commit and say
so.

That also changes what failure means. The rollback above exists because no commit had landed yet;
here one has. **Do not roll back on a second-pass failure** — report the split state instead: the
ticket is behind the code by exactly the criteria the user just confirmed, so say which ones.
