---
name: to-commit
description: Commit a completed ticket as one Conventional-Commit, verifying each acceptance criterion, then ticking it off on the ticket itself. Proposes closing the ticket, but never closes it without the user's say-so. Invoked by /implement at the end of a ticket session.
disable-model-invocation: true
---

# To Commit

Commit the current session's work as **one commit per ticket**, then record the verified
acceptance criteria back onto the ticket.

**The user decides; this skill executes.** It never closes a ticket, never pushes, and never
ticks a box it could not verify by execution. But once the user answers, it carries out every
remaining step without further prompting.

The whole value of this skill is that an `[x]` on a ticket can be trusted. A missing tick gets
noticed and complained about; a wrong tick is a lie that sits on the ticket forever and nobody
re-checks. So the standing rule is **when in doubt, don't tick — and say why**.

The issue tracker should have been provided to you — run /setup-matt-pocock-skills if not.
Read `docs/agents/issue-tracker.md` first: which commands to use depends on which tracker this
repo configured, and **the step order below differs between remote and local trackers**.

## Process

### 1. Identify the tickets

Usually already in context from /implement. A session may have completed **several** tickets —
list them and order by dependency (blockers first). If nothing is in context, ask.

One commit per ticket. Prefactoring is the only exception (step 2).

### 2. Peek at house style, split out prefactoring

Read the repo's recent `git log` for an established convention — scope vocabulary, tense,
casing. Local convention outranks the template below.

If the session prefactored before building ("make the change easy, then make the easy change"),
land that as its own `refactor(...)` commit first.

### 3. Verify the acceptance criteria

Walk each ticket's criteria one by one. Sort each into one of two kinds — this split drives
everything downstream:

- **Execution-verified** — you ran something and observed the outcome (a test, the actual
  behaviour). You judge these yourself.
- **Reading-verified** — you read the code and it looks right. **Never tick these yourself.**
  Collect them for step 4.

Every tick you make carries a one-line piece of evidence (which test, what you did). That
evidence goes in the **session output only** — never into the ticket, never into the commit
message.

**Re-runs.** A ticket may span several sessions, so you will meet criteria already marked
`[x]`. Later work can break earlier work:

- Re-run **all** execution verification, including already-ticked criteria. If one now fails,
  **untick it and say so loudly**: `⚠ #42 的「POST /items 返回 201」上一轮已通过，本轮
  items.test.ts 失败，已取消勾选`. A tick that is no longer true is a lie on the ticket;
  removing it is correct even though it moves the ticket backwards.
- Do **not** re-ask reading-verified criteria the user already confirmed. Leave them ticked.

**A ticket with no acceptance criteria at all** (hand-filed issues often have none): degrade
gracefully. Tick nothing, commit as normal, and state plainly that
`#42 没有验收标准区块，未做勾选写回`. **Never invent criteria** from the work you just did —
that is setting your own exam, sitting it, and marking it.

### 4. Ask the user — question ①

**Skip this entirely when every criterion was execution-verified.** Otherwise, per ticket,
before its commit (the answer decides what the commit message says):

```
#42 —— 已执行验证通过：
  · POST /items 返回 201 且落库   （items.test.ts 全绿）
  · 列表页加载时展示骨架屏       （手动跑起来看过）

以下无法执行验证，需你确认（默认不勾）：
  · README 已更新                （改了 README.md 的「安装」一节）
  · 命名与领域词汇一致           （沿用 CONTEXT.md 的 Item / Batch）

确认哪几条？
```

**Local-markdown tracker only:** merge question ② (step 6) into this one — see step 6 for why.

If a criterion stays unmet, committing anyway needs the user's explicit say-so, and the reason
goes in the commit message.

### 5. Commit

Compose from the template below and commit to the current branch, one commit per ticket, in
dependency order.

Never use a closing keyword (`Closes`/`Fixes`): it only fires when the commit reaches the
default branch, and this skill does not push.

### 6. Ask the user — question ②

**Remote trackers (GitHub/GitLab) only.** Asked **once, after every commit has landed**, so the
user sees the whole picture with real shas rather than being chased ticket by ticket:

```
#41  abc1234  4/4 全部通过
#42  def5678  3/4（「并发写入不丢单」未通过）

分支 feat/foo，均未推到远程。要关闭哪些？
```

Get the push state from `git branch -r --contains <sha>` — empty means local-only. This is
**information for the user's decision, not a gate**. "还没推到远程" is the commonest reason to
answer "先别关", so it must be on screen — but the skill neither blocks on it nor offers to
push. **Pushing is never this skill's action.**

**Local markdown has no separate question ②.** A local ticket rides in the same commit as the
code, so it can never disagree with it, and there is no post-commit fact to report — no sha to
cite (the ticket file is *in* that commit), no push state worth gating on. Fold "要关闭吗?"
into question ① and land the tick, the `Status:` change, and the comment all in the commit.

### 7. Write back

Only after the user has answered. See "Write-back by tracker" for the commands.

1. **Re-read the ticket body** from the tracker. Align against **that** copy, not the one in
   your context — the ticket may have been edited since. This also stops two concurrent
   sessions from clobbering each other with a stale whole-body overwrite.
2. **Flip only boxes inside the acceptance-criteria region.** A ticket carries other
   checkboxes — task lists, sub-issue lists, hand-written todos — and they look identical.
   Never touch a box outside the region, however much it resembles a criterion.
3. **Mismatch means stop.** A criterion on the ticket you did not verify → leave `[ ]` and
   report it. Something you verified that has no matching criterion on the ticket → **stop,
   write nothing back, and tell the user**. Never fuzzy-match: the case that triggers it is
   exactly the case where a human edited the ticket, i.e. the case you least want a model
   guessing at.
4. **Append a comment** recording what happened (template below). The body is mutable state
   that gets rewritten every run; the comment log is the only append-only record — and it is
   the only place an untick from step 3 leaves a trace.
5. **Close** only the tickets the user named in question ②.

**On failure, stop — do not retry.** These writes fail because of permissions, a deleted
ticket, or a concurrent edit; retrying produces the same error later. Report how far you got,
give a paste-ready command, and **keep the temp body file** — it is the most expensive artefact
of the run:

```
⚠ 已提交 abc1234，但 #42 的 body 写回失败（403）。ticket 未被修改。手动补：
  gh issue edit 42 --body-file /tmp/.../issue-42.md
```

Never skip a failed step and carry on: a ticket that got closed but not ticked, or commented
but not updated, contradicts itself.

## Templates

Commit messages, ticket comments and the questions above are **written in Chinese** — they are
read by people. This file is not; it is instructions to a model. `Refs:` is a git trailer key
and the `feat`/`fix` prefixes are format, so both stay as they are.

<commit-template>

<type>(<scope>): <祈使句摘要，取自 ticket 标题>

<一到两行：这个 commit 交付的端到端行为，取自 ticket 的「What to build」>

本次验证通过:
- <条目>
- <条目>

未完成（用户签字放行）:
- <条目> —— <理由>

Refs: #<ticket id>

</commit-template>

Template notes:

- Only what **this commit** delivered — not a snapshot of the whole ticket. Ticket state is
  mutable; a commit message is not, and storing mutable state somewhere immutable guarantees it
  rots. Across a three-commit ticket you would otherwise get three conflicting half-lists.
- **No `- [ ]` / `- [x]` marks.** Checkboxes belong to the ticket. A commit states facts.
- The "未完成（用户签字放行）" section must survive: it records a *human decision*, and git is
  the only place that still remembers who waved it through and why once the ticket is closed,
  edited, or deleted.
- `scope` only if the repo's log shows an established scope vocabulary; otherwise omit.
- **Local-markdown tracker:** no issue ids — use `Refs: .scratch/<feature-slug>/issues/03-<slug>.md`.

<comment-template>

abc1234 (feat/foo)

执行验证通过：POST /items 返回 201 且落库；列表页展示骨架屏
用户确认：README 已更新
回归撤勾：并发写入不丢单（上一轮通过，本轮 items.test.ts 失败）

</comment-template>

Omit any line that does not apply. When the user closes the ticket, append `全部通过，关闭。`
to this same comment rather than posting a second, thinner one. On a local-markdown ticket,
drop the sha from the first line and keep the branch — the file is *in* that commit, so
`git log --follow` recovers it.

## Write-back by tracker

The ticket is the source of truth for state; the commit message records what each commit
delivered. They carry different things and neither is generated from the other.

**GitHub.** Re-read, flip, write back, comment, then close only if the user said so:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only:  - [ ] …  →  - [x] …
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue comment <n> --body "<comment-template>"
gh issue close <n>          # only when the user said to close
```

The acceptance-criteria region runs from the `## Acceptance criteria` heading to the next
heading of the same level. Match each criterion by its text within that region. Never
regenerate the body from the commit message — that would drop everything else the ticket carries.

**GitLab.** Same shape with `glab`:

```bash
glab issue view <n> -F json | jq -r .description > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only
glab issue update <n> --description "$(cat "$TMPDIR/issue-<n>.md")"
glab issue note <n> --message "<comment-template>"
glab issue close <n>        # only when the user said to close
```

**Local markdown.** One file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`.
Edit it with the Edit tool **before** `git commit` and stage it with the code — the tick and the
work that earned it belong in one commit.

- The acceptance-criteria region is the **top-level** checkboxes below the `**Status:**` line
  (`/to-tickets`' local template has no heading for them). Do not descend into nested items.
- Append the comment to a `## Comments` heading at the bottom of the file, per
  `issue-tracker-local.md`.
- On close, set `**Status:** resolved` — the word `issue-tracker-local.md` already uses for a
  finished local ticket. Leaving a fully-ticked ticket at `ready-for-agent` actively advertises
  work that no longer exists. If the user does not close, leave `Status:` untouched.

If the commit has already been made, do not amend — land the ticket edit as a follow-up
`chore:` commit and say so.
