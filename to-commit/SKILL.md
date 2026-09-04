---
name: to-commit
description: Commit a completed ticket as one Conventional-Commit, verifying each acceptance criterion, then ticking it off on the ticket itself. Pushes the branch and closes the ticket only once every criterion is earned. Invoked by /implement at the end of a ticket session.
disable-model-invocation: true
---

# To Commit

Commit the current session's work as **one commit for one ticket**, then record the verified
acceptance criteria back onto the ticket. The tree was clean before /implement started, so
everything in it belongs to this ticket — no hunk-picking, no grouping judgement.

An `[x]` is a claim that somebody checked, and a wrong one is a lie that sits on the ticket
forever. So every tick this skill writes is **earned**: you ran something and watched it pass.
Unearned criteria stay `[ ]` and get reported. **When in doubt, don't tick — and say why.**

**Closing is earned too.** A ticket closes when every one of its criteria is earned and not
before — arithmetic on the ticks, never a judgement call — so the same evidence that fills the
last `[ ]` is what pushes the branch and closes the ticket in step 7. The user's own decision
survives where it belongs: the one question in step 5. Once they answer it, carry out every
remaining step without further prompting.

## Which tracker

Read `docs/agents/issue-tracker.md` first, then read only the write-back file it points to —
**that choice flips the order of operations in step 4**. If the file is missing, run
/setup-matt-pocock-skills.

- **GitHub or another external tracker** → [write-back-remote.md](write-back-remote.md)
- **Local markdown** → [write-back-local.md](write-back-local.md)

## Process

### 1. Identify the ticket

One ticket, one commit — though a ticket legitimately comes back for a second run, which step 3
covers. If the session spans more than one ticket, stop and say so.

### 2. Peek at house style

Read the repo's recent `git log` for scope vocabulary, tense, casing. Local convention outranks
the template below.

### 3. Sort the acceptance criteria

Walk the ticket's criteria one by one. Each is one of two kinds:

- **`ran`** — you executed something and watched the outcome: a test, the actual behaviour.
  Earned, so you tick them yourself in step 4.
- **`read`** — you only read the code and it looks right. Earned by the user's word alone, so
  they go to step 5 and stay `[ ]` until it arrives.

Every tick carries a one-line piece of evidence: which test, what you did. Evidence lives in the
**session output only** — the ticket and the commit message carry none of it.

**Re-runs.** You will meet criteria already marked `[x]`. Re-run **all** of the `ran`
verification, those included. One that now fails loses its tick, loudly:
`⚠ #42 的「POST /items 返回 201」上一轮已通过，本轮 items.test.ts 失败，已取消勾选`. Moving the
ticket backwards is right; leaving a tick that stopped being true is not. A ticket an earlier
run closed comes back open with the tick it lost — your tracker's file says how. Criteria the
user already confirmed keep theirs — those are asked once, not every run.

**A ticket with no acceptance criteria at all** (hand-filed issues often have none): tick
nothing, commit as normal, and state it plainly — `#42 没有验收标准区块，未做勾选写回`. The
criteria are the ticket's, never yours: writing your own is setting your own exam, sitting it,
and marking it.

### 4. Land the commit and the first write-back

Two operations, one invariant: **they succeed together or neither does.** An earned `[x]` must
never outlive the commit that earned it, and code must never land in a commit whose ticket did
not come with it. That rule is why the order flips by tracker:

- **Remote tracker** — the ticket lives outside the repo. **Commit, then write back.** A failed
  write-back leaves a split state: the commit has landed and stays landed, so report it honestly.
- **Local markdown** — the ticket file is *in* the repo, so it belongs in the same commit.
  **Write back, then commit.** Any failure rolls the ticks back and commits nothing.

Your tracker's file spells out its half.

#### Committing

If the staging area is **not** empty when you arrive, that contradicts the clean-tree
assumption: show the user what is already staged and let them decide. Otherwise stage everything
and make one commit on the current branch from the template below.

Leave `Closes`/`Fixes` out: step 7 closes the ticket itself, and only once every criterion is
earned. A trailer would hand that off to whoever merges the branch, on evidence nobody checked.

**When the commit itself fails**, it is almost always a pre-commit hook, in one of two kinds:

- **The hook rewrote files** (`lint-staged --fix`, prettier, a formatter). The work is fine, the
  hook just moved it. Re-stage and retry **once** — a hard limit, never a loop. Report which
  files it touched and that they are in the commit.
- **The hook refused** (tests red, types broken, an unfixable lint error). Stop, and show the
  hook's own output verbatim. The hook is the user's gate and this skill has no standing to open
  it, so `--no-verify` is off the table. A retry that fails again counts as a refusal.

A refusal leaves the tree holding everything /implement produced, so there is nothing to undo —
except on local markdown, where the invariant sends you to roll the ticks back first.

```
⚠ #03 未提交：pre-commit 失败

  items.test.ts → 2 failed

已回滚 ticket 勾选，文件恢复原样。修复后重跑 /to-commit。
```

#### The write-back

Tick the `ran` criteria and append a comment.

1. **Re-read the ticket body** from the tracker and align against *that* copy, not the one in
   your context — it may have been edited since, and a stale whole-body overwrite clobbers
   whoever edited it.
2. **Flip only boxes inside the acceptance-criteria region.** A ticket carries other checkboxes —
   task lists, sub-issue lists, hand-written todos — that look identical. Your tracker's file
   defines where the region begins and ends; every box outside it stays as it is.
3. **Match by exact text, and a mismatch stops the run.** A criterion on the ticket you did not
   verify → leave `[ ]` and report it. Something you verified with no matching criterion →
   **stop, write nothing back, and tell the user.** Fuzzy-matching fires exactly when a human
   edited the ticket — the case you least want a model guessing at.
4. **Append a comment** recording what happened (template below). The body is mutable state; the
   comment log is the only append-only record, and the only place an untick leaves a trace.

**On failure, stop.** These writes fail on permissions, a deleted ticket, or a concurrent edit,
and a retry produces the same error later. Every step runs or the run stops: a ticket that got
commented but not updated contradicts itself. Your tracker's file gives the wording.

### 5. Ask the user

**Only when `read` criteria exist.** All green means there is nothing to ask: report, then step 7.

```
#42 已提交 abc1234（分支 feat/items，未推送）
issue 已勾选 2 条并追加评论。

以下 2 条只读了代码、未执行验证，暂未勾选：
  · README 已更新          （改了 README.md 的「安装」一节）
  · 命名与领域词汇一致      （沿用 CONTEXT.md 的 Item / Batch）

这两条你认可吗？
```

Ask about the criteria and nothing else — they are what the rest of the run turns on.

### 6. Write back — second pass

Only after the user has answered, and only for the criteria they confirmed — their word is what
earns those. Same four rules, plus a second comment for the confirmation.

A commit has landed on every tracker by now, carrying the first-pass ticks. So a second-pass
failure is always a split state, never a rollback: report which criteria the ticket is behind by.

### 7. Push and close

**Only when the ticket is all green**: its acceptance-criteria region is non-empty and every box
inside it is `[x]`. Boxes outside the region never counted and still don't. An empty region — the
hand-filed ticket with no criteria — never goes green, so it is never pushed and never closed.

Both paths arrive here: step 4 when every criterion was `ran`, step 6 when the user's word earned
the rest. One criterion they declined leaves the ticket short of green; the commit and the
write-back stand, and nothing is pushed or closed.

**Push, then close, in that order.** The two cannot be atomic, so the order decides which half a
failure leaves standing. Code pushed with the ticket still open is a todo somebody can act on; a
closed ticket whose code never left the machine is a lie.

`git push -u origin <current branch>` the first time, `git push` after. Any branch — the closing
comment records which one, so a ticket closed from an unmerged branch says so on its face.

**No remote, or no upstream** — a shape, not a failure, and the shape a local-markdown repo
usually has. Skip the push, close as normal, and say so: `本仓库无远端，未推送`.

**A push that is refused** — a non-fast-forward, a protected branch, a pre-push hook — stops the
run with the ticket left open. The commit has landed and stays landed. `pull --rebase` rewrites
the commit this session just made and `--force` is off the table, so report the refusal, hand
back the command to retry by hand, and leave the remote alone: it is the user's gate, exactly as
a pre-commit hook is.

Your tracker's file carries the closing half.

## Templates

Commit messages, ticket comments and the question in step 5 are **written in Chinese** — people
read them. This file is not; it is instructions to a model. `Refs:` is a git trailer key and the
`feat`/`fix` prefixes are format, so both stay as they are.

<commit-template>
<type>(<scope>): <祈使句摘要，取自 ticket 标题>

<一到两行：这个 commit 交付的端到端行为，取自 ticket 的「What to build」>

本次验证通过:
- <条目>

本次未执行验证:
- <条目>

Refs: #<ticket id>
</commit-template>

- Include `<scope>` only where the repo's log shows an established scope vocabulary.
- Drop "本次未执行验证" entirely when every criterion was `ran`. Where it appears it states a fact
  about this commit — these criteria were not exercised — and claims no sign-off from anyone.
- The message states what **this commit** delivered, in plain facts with no `- [ ]` / `- [x]`
  marks: checkboxes belong to the ticket. A reworked ticket spans several commits, so a snapshot
  of the whole ticket would leave you three conflicting half-lists.

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
