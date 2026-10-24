# Scenarios

Each scenario runs in an isolated context that reads only this skill's files and the scenario. The
repo's `docs/agents/issue-tracker.md` configures GitHub; the tree was clean before /implement
started. Describe every command you would run and the final state of the commit, branch, remote,
and ticket. Do not run anything. Expected answers live in [expectations](expectations.md).

## A: All criteria ran green

Ticket #42 has `## Acceptance criteria` with three criteria. All three were run this session and
passed. The current branch is `feat/items`, with no upstream.

## B: A criterion that needs the PR's own CI

Ticket #206's region has six criteria. Five were run and passed. The sixth reads "PR 在自身提交上通过真实
CI 全套 check 与 process-trace"; no PR exists yet. The branch is `codex/issue-206`.

## C: No acceptance region

Ticket #226 has headings 目标与状态, 现有摩擦与证据, 深化方向 and no `## Acceptance criteria`. The work
is done and its tests pass. The branch is `for-226`.

## D: Regression on a closed ticket

Ticket #42 is CLOSED; every box is `[x]`. A re-run on new commits finds "并发写入不丢单" now fails
in `items.test.ts`. The other criteria still pass.

## E: Reading criteria

Ticket #43 has two `ran` criteria that passed and one criterion "README 已更新" that you only read.
The user confirms it after the question.
