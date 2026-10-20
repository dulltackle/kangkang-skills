# Performance work

Continue authorized performance work until the agreed acceptance criteria are met. Periodic and low-gain reviews guide the next action; they do not require renewed authorization. Once criteria are earned, proceed to acceptance and delivery. When progress stalls, follow the entry point's [reporting protocol](progress.md).

Create one shared `phaseId` and persist it outside the repository. Analysis, implementation, and experiments share cumulative active time. Agent changes, parallel work, and context compaction preserve the phase and its evidence. Exclude only explicit user waits and external blocks, recording their start, end, and reason.

Use `scripts/workflow.py --state <absolute-path> --run-id <run-id> budget --input <event.json>`. Each event includes `phaseId`, `event`, and the actual timestamp `at` with a timezone. Each incoming agent queries `status` first. `start` defaults to `mode:autonomous`, no time limit, and `checkpointMinutes:30` as the review interval. `pause` uses reason `user-wait` or `external-block`; `resume` ends the pause. `status` reports elapsed time, review reasons, pending decisions, and whether new experiments are allowed.

**Legacy recovery:** when a saved phase lacks current policy metadata or `status` returns `decision:reconcile`, read [legacy performance recovery](performance-recovery.md).

## Progress reviews

Assess measurement reliability, gains, remaining acceptance gaps, and the next experiment's rationale. Report material findings while continuing work. Record `review` with a concise `summary`, concrete `nextAction`, and original evidence `source`. This acknowledges current signals and schedules the next review after another interval of active time, preserving cumulative time and measurements.

`measure` includes a positive `durationSeconds`, `completeEntry`, `comparisonKey`, and the original measurement `source`. Hold the complete entry point, source scope, model, environment, cache state, and concurrency conditions fixed. Three consecutive complete measurements with the same comparison identity establish two improvement rounds. An incomplete or incomparable sample breaks the sequence.

Two rounds below 5%, including regressions, flag an early review. Interpret the signal against measurement noise and the acceptance gap: profile the remaining bottleneck, revise the hypothesis, or change the approach. Give repeated experiments a concrete verification purpose. A recorded review consumes the current signal; another low-gain signal requires three new comparable samples. Preserve unresolved stall records even when the review signal clears. Reviews leave experiment authorization and acceptance criteria unchanged.

## User budgets

A hard time budget applies only when the user sets one. Start with `mode:bounded`, positive `limitMinutes`, and `source` containing the user's exact instruction; the coordinator verifies that it establishes a limit. A review interval may exceed a short budget. At the limit, stop new experiments covered by that budget and present gains, gaps, and the next proposed action. Continue only work outside the limit's scope; an overall task limit also covers repair, review, and independent work.

`decide` records the user's `choice` and original `source`. `continue` requires positive `extensionMinutes` for a bounded phase; `autonomous` removes the time limit with the user's authorization; `phase` preserves a user-selected phase delivery. Keep measurements and decision history. Neither a review nor a repeated `start` renews a budget. A policy update does not resume a phase the user chose to stop, and authorization does not end an outstanding pause: record `decide` or `resume` as appropriate after resolving the reason.
