# Behavioral regression expectations

When evaluating skill changes, give an isolated agent only `SKILL.md`, necessary references, and `scenarios.md`; ask it to report scheduling decisions. Keep this evaluator file out of its context. Use no real tracker connections, real implementation dispatches, or external writes. Evaluate each decision rather than keyword counts.

- **A:** Discover 43, 44, 45, and 46; exclude background ticket 70. Tickets 43 and 46 are ready; 44 and 45 wait for 43.
- **B1, B2, B3:** Stop all implementation in every case, including active implementers. Stop new dispatches, merges, write-back, and handoff. Preserve work. Recover the failed query, complete pagination, or restore access, then rediscover and verify before resuming.
- **C:** Add all four tickets. Preserve `abc`; map each ticket to commits, review, acceptance, and write-back evidence. Complete missing work and final verification. Parent review and acceptance cannot substitute for child-ticket evidence; preserve existing implementation rather than recreating per-ticket commits.
- **D:** Include 46 and return to reconciliation, missing implementation or review, and acceptance. Keep the PR in draft and full-spec closure and completion claims pending.
- **E:** Leave 46 unaccepted; parent reading confirmation cannot replace executable checks. Block handoff, record the parent's actual closed state, and correct it under tracker rules and authorization.
- **F:** Ask the user to resolve 43's conflicting parentage, blocking affected paths and full delivery. Ticket 44 is confirmed independent and may proceed. Ticket 45 is only a reference and remains excluded.
- **G:** Leave 81 unchecked; prefer a deterministic import check, since implementer assertions are insufficient. Accept 82 as `reviewed` without another user confirmation. Keep 83 and 84 pending user confirmation. Keep 85 unexecuted; user confirmation cannot replace execution. Clarify 86's behavior criterion before acceptance. Batch only items needing user decisions.
- **H:** Supplement 91 with independent technical review rather than automatically upgrading its classification. Review 92's affected content at `def`. Identical fingerprints for 93 do not prove fixed source; rerun formal checks in a separate checkout. Evidence for 94 verifies only `def`; formally reverify `ghi` and reconcile affected criteria before delivering it. A skill update alone does not retroactively change earlier acceptance or closure state.

Report actual output against each expectation. If the old version also passes a case, that shows the agent supplied the missing reasoning in that run; it does not establish reproduction of an old failure. These scenarios verify decisions, not real API behavior, concurrent pausing, or end-to-end implementation.
