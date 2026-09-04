# Write-back — local markdown tracker

For repos whose `docs/agents/issue-tracker.md` configures **local markdown**. One file per ticket
under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.

The ticket file is *in* the repo, so it goes into the same commit as the work. **Edit it with the
Edit tool before `git commit`** and stage it with the code.

## The acceptance-criteria region

`/to-tickets`' local template gives the criteria no heading, so shape delimits the region:

- **It starts** at the first checkbox below the `**Status:**` line.
- **It ends** at the first line that is neither a checkbox nor blank — prose, a heading, anything.
- **Nested checkboxes** neither end the region nor get ticked. Step past them.

```markdown
**Status:** ready-for-agent

- [ ] 标准 1          ← region starts
  - [ ] 子项           ← skipped, region continues
- [ ] 标准 2          ← region ends here

随手记的备忘：       ← terminator
- [ ] 手写 todo       ← outside; never touched
```

This cuts the region short rather than long on purpose. A stray line between criteria costs a
tick you then report as unverified; the other way round silently ticks somebody's todo list. A
lost tick is visible — when in doubt, don't tick.

## The comment

Append it under a `## Comments` heading at the bottom of the file, per the local conventions in
`docs/agents/issue-tracker.md`. **The template does not create that heading** — on a ticket's
first write-back it will not be there, so add it at the end of the file, then append under it.

The `**Status:**` line stays as it is on any run that leaves a criterion unticked. An all-green
ticket sets it, below.

## Closing an all-green ticket

A local ticket has no close command: the `**Status:**` line **is** the close. Set it to `done`.

`done` is this skill's own word. `docs/agents/issue-tracker.md` describes the `Status:` line
without listing it, so a reader of that file meets `done` here first.

**Which commit carries it depends on the path.** Step 4's write-back runs before the commit, so
on the all-`ran` path `Status: done` rides in the same commit as the work — the ticket file is in
the repo and belongs with it. On the step-6 path the commit has already landed, so the second
pass's `chore:` commit carries it instead. That extra commit is what the no-amend rule costs, not
a shape to copy back onto the first path.

Step 7 pushes afterwards either way, and a repo with no remote skips the push and stays closed —
no remote is the shape a local-markdown tracker usually comes in.

**Reopening.** When a re-run unticks a criterion, `**Status:**` goes back to `ready-for-agent`
beside the untick.

## Rolling back

Whenever a local run stops before its commit lands — a hook refusing, a mismatch, a write failure
— the ticks already written come back off, and any `done` with them.

```bash
git checkout -- .scratch/<feature-slug>/issues/<NN>-<slug>.md
```

**The path is mandatory and it is one file.** `git checkout .`, `-- .`, `git restore .` and `-A`
are all forbidden here: widening this command past the single ticket file destroys the session's
entire work — the exact work sitting uncommitted in the tree at the moment you run it.

Nothing else is lost. The tree still holds everything /implement produced, so the user fixes the
cause and re-runs.

```
⚠ #03 写回失败：ticket 上有「并发写入不丢单」，但本轮未验证到对应项。
  未做任何修改，未提交。工作树原样保留，请确认 ticket 后重跑 /to-commit。
```

**Rollback only reaches a tracked file.** On a ticket's first run the file is usually untracked —
`/to-tickets` writes ticket files but never commits them, so nothing is tracked until this skill's
own first commit, and `git checkout` fails with `pathspec did not match`. That is expected: leave
the edits in place and say plainly what was written, so the user can undo it by hand.

```
⚠ #03 未提交。ticket 文件尚未纳入版本控制，无法回滚。
  已写入：勾选了 2 条验收标准。请手动确认后重跑。
```

## Template variations

- **Commit message** — no issue ids. Use `Refs: .scratch/<feature-slug>/issues/<NN>-<slug>.md`.
- **Comment** — drop the sha from the first line, keep the branch. The file is *in* that commit,
  so `git log --follow` recovers it. On an all-green run add a `已关闭：验收标准全部通过` line.
  The push itself is reported in the session output, since the comment is written before it
  happens.

## The second pass

The commit has landed by now and carries the first-pass ticks. **Do not amend it** — land the
ticket edit as a follow-up `chore:` commit and say so. The rollback above existed because no
commit had landed; here one has, so a second-pass failure is reported as a split state instead:
name the criteria the ticket is behind by.
