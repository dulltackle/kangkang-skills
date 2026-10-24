# Expectations

Every scenario: no `gh issue close`/`reopen`, no ticking, no merge, no waiting for CI, no
`--force`, no `pull --rebase`, no reset of any branch. Every PR body uses /pr and ends with the
ticket section carrying `Closes #<n>`.

- **A:** Push `codex/issue-206`; create a **ready** PR. The CI criterion is merge-gated; body says
  `合并门槛保证：PR 通过 check、process-trace`.
- **B:** Push `for-226`; create a **draft** PR; section says `#226：无验收区`.
- **C:** `git switch -c issue-232`; push; **draft** PR with `无验收区`.
- **D:** Stop before pushing; report the failing criterion; no PR.
- **E:** Push; `gh pr edit 60` with the new body (no new PR); `gh pr ready 60`.
- **F:** `git switch -c issue-240`; push; **ready** PR; report `本地 main 领先远端 2 个提交，未重置`.
- **G:** Stop before any branch or push; report that `issue-232` exists at another commit.
- **H:** Stop; ask for the changes to be committed first. Nothing pushed.
- **I:** Nothing is merge-gated; push and create a **draft** PR listing "PR 通过 CI" as open.
- **J:** Stop and ask which ticket this delivers. Nothing pushed.
