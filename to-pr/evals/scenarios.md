# Scenarios

Each scenario runs in an isolated context that reads only this skill's files and the scenario. The
repo is `o/r` on GitHub, default branch `main`, and `docs/agents/issue-tracker.md` configures
GitHub. Unless a scenario says otherwise: the tree is clean, `HEAD` has commits ahead of
`origin/main` carrying `Refs: #<n>`, and main's protection requires `check` and `process-trace`.
Describe every command you would run, the PR's final state and body's ticket section, and the
report. Do not run anything. Expected answers live in [expectations](expectations.md).

## A: Last criterion is the PR's own CI (#206)

Branch `codex/issue-206`, no PR yet. #206's `## Acceptance criteria` has six boxes: five `[x]`,
and `[ ]` "PR 在自身提交上通过真实 CI 全套 check 与 process-trace".

## B: No acceptance region (#226)

Branch `for-226`, no PR. #226 has headings 目标与状态, 现有摩擦与证据, 深化方向 — no
`## Acceptance criteria`.

## C: Detached HEAD, no region (#232)

`HEAD` is detached at `8ce581d` with `Refs: #232`. #232 is a spec with `## Testing Decisions` but no
`## Acceptance criteria`. No branch named `issue-232` exists anywhere.

## D: A failing criterion

Branch `issue-42`. #42's latest comment, for the current `HEAD`, reads `回归撤勾：并发写入不丢单（本轮
items.test.ts 失败）`.

## E: Existing draft, now all green

Branch `issue-43` already has draft PR #60 whose ticket section lists one open criterion. Since
then that box on #43 was ticked; every box in the region is now `[x]`. A new commit is unpushed.

## F: Work committed on main

The current branch is `main`, two commits ahead of `origin/main`, both `Refs: #240`. #240 has a
region with every box `[x]`.

## G: Branch name taken

`HEAD` is detached with `Refs: #232`. `origin/issue-232` exists at a different commit.

## H: Uncommitted changes

Branch `issue-44` with modified, unstaged `src/a.ts`.

## I: Protection unreadable

Branch `issue-45`. `gh api .../protection/required_status_checks` returns 403 and the rulesets
endpoint returns an empty list. #45 has three `[x]` and `[ ]` "PR 通过 CI".

## J: No ticket reference

Branch `cleanup`, no arguments, and no commit carries a `Refs:` trailer.
