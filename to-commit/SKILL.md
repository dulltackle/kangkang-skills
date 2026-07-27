---
name: to-commit
description: Commit a completed ticket as one Conventional-Commit, verifying each acceptance criterion, then ticking it off on the ticket itself. Never closes the ticket and never pushes. Invoked by /implement at the end of a ticket session.
disable-model-invocation: true
---

# To Commit

Commit the current session's work as **one commit for one ticket**, then record the verified
acceptance criteria back onto the ticket.

The working tree was clean before /implement started, so everything in it now belongs to this
ticket. That is what makes the whole flow simple: no hunk-picking, no grouping judgement.

**The user decides; this skill executes.** It never closes a ticket — closing is the user's own
act, done by hand — and it never pushes. It never ticks a box it could not verify by execution
without asking first. But once the user answers, it carries out every remaining step without
further prompting.

The whole value of this skill is that an `[x]` on a ticket can be trusted. A missing tick gets
noticed and complained about; a wrong tick is a lie that sits on the ticket forever and nobody
re-checks. So the standing rule is **when in doubt, don't tick — and say why**.

## Which tracker

The issue tracker should have been provided to you — run /setup-matt-pocock-skills if not. Read
`docs/agents/issue-tracker.md` first: it decides which of the two write-back files below applies,
and **that choice changes the order of operations in step 4**.

- **GitHub, GitLab, or another external tracker** → [write-back-remote.md](write-back-remote.md)
- **Local markdown** → [write-back-local.md](write-back-local.md)

Read only the one that applies. Each carries its tracker's commands, how the acceptance-criteria
region is delimited, and what failure means there.

## Process

### 1. Identify the ticket

Usually already in context from /implement. If nothing is in context, ask.

One ticket, one commit. If the session somehow spans more than one ticket, stop and say so —
this skill commits one.

A ticket can legitimately come back for a second run (CI went red, you found a bug, you
reworked it). That is fine and expected; step 3 covers what changes on a re-run.

### 2. Peek at house style

Read the repo's recent `git log` for an established convention — scope vocabulary, tense,
casing. Local convention outranks the template below.

### 3. Verify the acceptance criteria

Walk the ticket's criteria one by one. Sort each into one of two kinds — this split drives
everything downstream:

- **Execution-verified** — you ran something and observed the outcome (a test, the actual
  behaviour). You tick these yourself, in step 4.
- **Reading-verified** — you read the code and it looks right. **Never tick these yourself.**
  Collect them for step 5.

Every tick you make carries a one-line piece of evidence (which test, what you did). That
evidence goes in the **session output only** — never into the ticket, never into the commit
message.

**Re-runs.** On a second run you will meet criteria already marked `[x]`. Re-run **all**
execution verification, including those. If one now fails, **untick it and say so loudly**:
`⚠ #42 的「POST /items 返回 201」上一轮已通过，本轮 items.test.ts 失败，已取消勾选`. A tick
that is no longer true is a lie on the ticket; removing it is correct even though it moves the
ticket backwards. Do **not** re-ask reading-verified criteria the user already confirmed —
leave them ticked.

**A ticket with no acceptance criteria at all** (hand-filed issues often have none): degrade
gracefully. Tick nothing, commit as normal, and state plainly that
`#42 没有验收标准区块，未做勾选写回`. **Never invent criteria** from the work you just did —
that is setting your own exam, sitting it, and marking it.

### 4. Land the commit and the first write-back

Two operations, and **the invariant is that they succeed together or neither does**: an `[x]`
must never outlive the commit that earned it, and code must never land in a commit whose ticket
did not come with it. The whole reason the order differs by tracker is to serve that one rule.

- **Remote tracker** — the ticket lives outside the repo. **Commit, then write back.** If the
  write-back fails the commit has already landed and cannot be unmade; report the split state
  honestly and never try to undo it.
- **Local markdown** — the ticket file is *in* the repo, so it has to be in the same commit.
  **Write back, then commit.** If anything fails at any point, roll the ticks back and commit
  nothing.

Your tracker's file spells out its half in full. Follow it.

#### Committing

Stage everything and make one commit. The tree was clean before /implement, so every change in
it is this ticket's — there is nothing to select between. If you arrive and the staging area is
**not** empty, that contradicts the assumption: show the user what is already staged and let
them decide before going on.

Compose the message from the template below and commit to the current branch.

Never use a closing keyword (`Closes`/`Fixes`): it only fires when the commit reaches the
default branch, and this skill does not push. **Pushing is never this skill's action.**

**When the commit itself fails.** A pre-commit hook rejecting the commit is far more common
than a write-back failure, and it comes in two kinds:

- **The hook rewrote files** (`lint-staged --fix`, prettier, a formatter). The work is fine;
  the hook just moved it. Re-stage and retry **once** — that is a hard limit, never a loop. Say
  in the report which files the hook touched and that they are in the commit.
- **The hook refused** (tests red, types broken, an unfixable lint error). Stop. Show the hook's
  own output rather than a paraphrase of it. **Never `--no-verify`** — the hook is the user's
  gate, and this skill does not have standing to open it. A retry that still fails counts as a
  refusal and lands here.

On a refusal the tree keeps everything /implement produced, so there is nothing to undo — the
one exception being a local-markdown run, where the invariant above sends you to roll the ticks
back before reporting.

```
⚠ #03 未提交：pre-commit 失败

  items.test.ts → 2 failed

已回滚 ticket 勾选，文件恢复原样。修复后重跑 /to-commit。
```

#### The write-back

Tick the execution-verified criteria and append a comment.

1. **Re-read the ticket body** from the tracker. Align against **that** copy, not the one in
   your context — the ticket may have been edited since. This also stops two concurrent
   sessions from clobbering each other with a stale whole-body overwrite.
2. **Flip only boxes inside the acceptance-criteria region.** A ticket carries other
   checkboxes — task lists, sub-issue lists, hand-written todos — and they look identical.
   Never touch a box outside the region, however much it resembles a criterion. Your tracker's
   file defines where the region begins and ends.
3. **Mismatch means stop.** A criterion on the ticket you did not verify → leave `[ ]` and
   report it. Something you verified that has no matching criterion on the ticket → **stop,
   write nothing back, and tell the user**. Never fuzzy-match: the case that triggers it is
   exactly the case where a human edited the ticket, i.e. the case you least want a model
   guessing at.
4. **Append a comment** recording what happened (template below). The body is mutable state
   that gets rewritten every run; the comment log is the only append-only record — and it is
   the only place an untick from step 3 leaves a trace.

**On failure, stop — do not retry.** These writes fail because of permissions, a deleted
ticket, or a concurrent edit; retrying produces the same error later. Never skip a failed step
and carry on: a ticket that got commented but not updated contradicts itself. What "stop" means
here — a split-state report or a rollback — depends on where the commit is, which is what the
ordering above decided; your tracker's file gives the exact wording.

### 5. Ask the user

**Only when reading-verified criteria exist.** All-green means there is nothing to ask — report
the result and stop.

```
#42 已提交 abc1234（分支 feat/items，未推送）
issue 已勾选 2 条并追加评论。

以下 2 条只读了代码、未执行验证，暂未勾选：
  · README 已更新          （改了 README.md 的「安装」一节）
  · 命名与领域词汇一致      （沿用 CONTEXT.md 的 Item / Batch）

这两条你认可吗？
```

Do not ask about closing the ticket. Closing is the user's own act and no business of this
skill's.

### 6. Write back — second pass

Only after the user has answered, and only for the criteria they confirmed. Same four rules as
the first pass: re-read the body, flip only inside the region, stop on mismatch or failure.
Append a second comment for the confirmation — it records a real change to the checkboxes, so it
earns its own entry in the log.

By now a commit has landed on every tracker, and it carries the first-pass ticks. So a
second-pass failure is always a split state, never a rollback: report which criteria the ticket
is now behind the code by.

## Templates

Commit messages, ticket comments and the question above are **written in Chinese** — they are
read by people. This file is not; it is instructions to a model. `Refs:` is a git trailer key
and the `feat`/`fix` prefixes are format, so both stay as they are.

<commit-template>
<type>(<scope>): <祈使句摘要，取自 ticket 标题>

<一到两行：这个 commit 交付的端到端行为，取自 ticket 的「What to build」>

本次验证通过:
- <条目>
- <条目>

本次未执行验证:
- <条目>

Refs: #<ticket id>
</commit-template>

Template notes:

- Only what **this commit** delivered — not a snapshot of the whole ticket. Ticket state is
  mutable; a commit message is not, and storing mutable state somewhere immutable guarantees it
  rots. A reworked ticket spans several commits, and you would otherwise get three conflicting
  half-lists.
- "本次未执行验证" states a fact about this commit — that these criteria were not exercised. It
  does not claim anyone signed them off; at commit time nobody has. Omit the section when every
  criterion was execution-verified.
- **No `- [ ]` / `- [x]` marks.** Checkboxes belong to the ticket. A commit states facts.
- `scope` only if the repo's log shows an established scope vocabulary; otherwise omit.

First-pass comment. Omit any line that does not apply:

<comment-template>
abc1234 (feat/foo)

执行验证通过：POST /items 返回 201 且落库；列表页展示骨架屏
回归撤勾：并发写入不丢单（上一轮通过，本轮 items.test.ts 失败）
待人工确认：README 已更新；命名与领域词汇一致
</comment-template>

Second-pass comment:

<comment-template-2>
用户确认：README 已更新；命名与领域词汇一致
</comment-template-2>

A local-markdown tracker varies both templates slightly — see its file.
