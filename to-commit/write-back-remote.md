# Write-back — remote trackers

For repos whose `docs/agents/issue-tracker.md` configures **GitHub** or another external tracker.
The ticket lives outside the repo, so the commit lands first and the write-back follows it.

The ticket is the source of truth for state; the commit message records what each commit
delivered. Neither is generated from the other — the ticket body is edited in place, and
regenerating it from the commit message would drop everything else the ticket carries.

## The acceptance-criteria region

The region runs from the `## Acceptance criteria` heading to the next heading of the same level.
Match each criterion by its text within that region.

## GitHub

Re-read, flip, write back, comment:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only:  - [ ] …  →  - [x] …
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue comment <n> --body "<comment-template>"
```

## Closing an all-green ticket

Step 7 has pushed by the time you get here. Close with a comment of its own:

```bash
gh issue close <n> --comment "<close-template>"
```

The body is mutable state and its `[x]` marks can be edited by anyone; the comment log is the
only append-only record, which makes it the one place a closure leaves a trace of **what commit,
on what branch, closed this**.

<close-template>
abc1234 (feat/foo) 已推送

验收标准 4 条全部通过，关闭。
</close-template>

**Reopening.** A re-run that unticks a criterion on a ticket an earlier run closed reopens it,
alongside the untick and its comment:

```bash
gh issue reopen <n>
```

## Other trackers

GitLab, Jira, Linear, or anything else the user described in their own words: follow the workflow
written in `docs/agents/issue-tracker.md`. Everything above still applies — the region, matching
by text, stopping on a mismatch, and the split-state report below.

Where that file does not say how to edit a ticket body **or how to close a ticket**, **stop and
ask**. The command comes from that file and nowhere else: a wrong write to somebody's tracker is
worse than a run that stopped and reported.

One trap worth naming, because `gh issue close --comment` trains the wrong reflex: GitLab splits
the close in two, a note then a close. Take both commands from `docs/agents/issue-tracker.md`.

## On failure — report the split state

The commit has landed and stays landed. Report honestly: what landed, what did not, what is left
to do by hand. Give a paste-ready command and **keep the temp body file** — it is the most
expensive artefact of the run.

```
⚠ 已提交 abc1234，但 #42 的 body 写回失败（403）。ticket 未被修改。手动补：
  gh issue edit 42 --body-file "$TMPDIR/issue-42.md"
```

A **mismatch** lands here too: write nothing back and report it the same way.

A refused **push** stops the run before the close, leaving the ticket open — which is the state
it should be in:

```
⚠ 已提交 abc1234，推送被拒（远端有新提交）。#42 保持开启。
  拉取后手动重试：git pull && git push
```

A failed **close** leaves the widest split of all: the code is public, the ticket still says open.

```
⚠ abc1234 已推送，但 #42 关闭失败（403）。验收标准已全部勾选，issue 仍开启。手动补：
  gh issue close 42
```
