---
name: to-pr
description: Deliver the current branch as a pull request that closes its tickets on merge — draft until every acceptance criterion is earned, ready once it is. Invoked by /implement after /to-commit; safe to re-run.
disable-model-invocation: true
---

# To PR

Put the current branch on the remote as **one PR for its tickets**. The body says `Closes #<n>`
from the start; **draft status is the gate**, since a draft cannot merge. The ticket closes when
the PR merges, and no step of this skill closes, reopens, or ticks a ticket.

Read state from git and the tracker, never from another skill's memory. Whoever committed the
work — /to-commit, another skill, or the user by hand — this skill does the same thing.

Re-running is normal: a PR that already exists for the branch is updated, never duplicated.

## Process

### 1. Identify the tickets

Read `docs/agents/issue-tracker.md` for how to read tickets. If it is missing, run
/setup-matt-pocock-skills.

Tickets come from the user's arguments. Without arguments, collect the `Refs: #<n>` trailers of
the commits on `origin/<default>..HEAD`. None found → stop and ask which ticket this delivers.

### 2. Check the tree

Stop and report, changing nothing, when:

- there is no remote — a PR needs one;
- the tree has staged or unstaged changes — commit them first (/to-commit);
- `HEAD` has no commits ahead of `origin/<default>` — there is nothing to deliver;
- this session saw a `ran` criterion fail on the current commit, or the ticket's latest comment
  records one as failing (`回归撤勾` or an unticked criterion with a failing run). Failing work
  stays local.

### 3. Get onto a feature branch

- **A feature branch** → use it.
- **Detached `HEAD`** → `git switch -c issue-<n>`, `<n>` being the first ticket.
- **The default branch** → `git switch -c issue-<n>` the same way, and report that local
  `<default>` is now ahead of the remote by those commits. Never reset it: moving the user's
  branch back is their call.

If `issue-<n>` already exists, locally or on the remote, at another commit → stop and report.
Never overwrite a branch.

### 4. Decide draft or ready

Re-read every ticket from the tracker. The acceptance-criteria region is the
`## Acceptance criteria` heading up to the next heading of the same level; boxes outside it never
count. Nothing else is a region — not another heading, not prose that reads like criteria.

Read the default branch's **required checks** — the merge gate:

```bash
gh api repos/{owner}/{repo}/branches/<default>/protection/required_status_checks --jq '.contexts'
gh api repos/{owner}/{repo}/rules/branches/<default>   # rulesets: type "required_status_checks"
```

An unticked criterion is **merge-gated** when its text asks for exactly this: this PR passing
some or all of those required checks. GitHub enforces it before merge, so it need not be earned
first. Unreadable protection or no required checks → nothing is merge-gated.

A ticket is **ready** when its region is non-empty and every box in it is `[x]` or merge-gated.
The PR is **ready** when every ticket is; otherwise it is a **draft**. No region, an unverified
criterion, one awaiting the user's word — all draft.

### 5. Write the body

Call the Skill tool with `pr` for the body. Append the ticket section from the template below.
Keep it short: the PR is a pointer to the tickets, not a copy of them.

### 6. Push

`git push -u origin <branch>` the first time, `git push` after.

**A refused push** — non-fast-forward, protected branch, pre-push hook — stops the run. Report it
and hand back the command to retry. `pull --rebase` rewrites the user's commits and `--force` is
off the table: the remote is the user's gate, exactly as a pre-commit hook is.

### 7. Open or update the PR

```bash
gh pr view --json number,url,isDraft          # does the branch have one?
gh pr create --base <default> --title "<title>" --body-file "$TMPDIR/pr-body.md" [--draft]
gh pr edit <pr> --body-file "$TMPDIR/pr-body.md"
gh pr ready <pr>             # draft → ready
gh pr ready <pr> --undo      # ready → draft, when a criterion lost its tick
```

Title: the commit subject when there is one commit, otherwise the ticket's title.

For another tracker or forge, take the equivalent commands from `docs/agents/issue-tracker.md`;
where it gives none, stop and ask.

Do not wait for CI and do not merge. Merging is the user's decision.

### 8. Report

```
PR #57（draft）https://github.com/o/r/pull/57 ← 分支 issue-42，已推送
#42 待完成：并发写入不丢单（未验证）
合并门槛保证：PR 通过 check
```

Add any line from step 3, such as `本地 main 领先远端 2 个提交，未重置`.

## Template

Written in Chinese — people read it. `Closes` is GitHub's keyword, so it stays as it is.

<ticket-section>
## 关联事项

Closes #42

- #42：验收 3/4 已勾选。待完成：并发写入不丢单（未验证）
- 合并门槛保证：PR 通过 check、process-trace
</ticket-section>

- One `Closes` line per ticket.
- Per ticket, one line: ticks earned, then what is still open and why. A ticket with no region
  says `无验收区`; one whose only open boxes are merge-gated says
  `验收 5/6 已勾选，其余 1 项由合并门槛保证`.
- Drop the merge-gate line when nothing is merge-gated.
