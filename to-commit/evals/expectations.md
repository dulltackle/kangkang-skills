# Expectations

Every scenario: no `git push`, no `gh pr`, no `gh issue close` or `gh issue reopen`. The report ends
by pointing at `/to-pr`. The commit carries `Refs: #<n>` and never `Closes`/`Fixes`.

- **A:** One commit, then re-read the body, tick all three, comment. Branch stays unpushed.
- **B:** Commit; tick the five that ran. The sixth stays `[ ]` as unverified (not `read`, not
  asked of the user) and is reported. Nothing is pushed — /to-pr decides delivery.
- **C:** Commit; no ticks and no invented criteria; state `#226 没有验收标准区块，未做勾选写回`.
  Nothing is pushed or closed.
- **D:** Commit; untick "并发写入不丢单" loudly and comment it as `回归撤勾`. The ticket stays
  CLOSED; report that reopening is the user's call.
- **E:** Commit; tick the two `ran` criteria; ask about "README 已更新" only; after the yes, tick it
  with a second comment. Still no push or close.
