# Collaboration and performance work

## Performance work

Continue authorized performance work until the agreed acceptance criteria are met. Review progress periodically and adjust the approach from evidence. Elapsed time and low gains call for reassessment; they do not require renewal of the user's authorization. Once criteria are earned, proceed to acceptance and delivery.

Create one shared `phaseId` and persist it outside the repository. Analysis, implementation, and experiments share cumulative elapsed time. Agent changes, parallel work, and context compaction preserve the phase and its evidence. Exclude only explicit user waits and external blocks, recording their start, end, and reason.

Use `scripts/workflow.py --state <absolute-path> --run-id <run-id> budget --input <event.json>`. Each event includes `phaseId`, `event`, and the actual timestamp `at` with a timezone. Each incoming agent queries `status` first. `start` defaults to `mode:autonomous`, no time limit, and `checkpointMinutes:30` as the recurring review interval. `pause` uses reason `user-wait` or `external-block`; `resume` ends the pause. `status` reports elapsed time, review reasons, pending user decisions, and whether new experiments are allowed.

### Progress reviews

At a review, assess measurement reliability, gains, remaining acceptance gaps, and the next experiment's rationale. Report material findings while continuing work. Record `review` with a concise `summary`, concrete `nextAction`, and saved evidence `source`. This acknowledges the current signals and schedules the next review after another interval of active time; it preserves cumulative time and measurements.

`measure` includes a positive `durationSeconds`, `completeEntry`, `comparisonKey`, and the original measurement `source`. Hold the complete entry point, source scope, model, environment, cache state, and concurrency conditions fixed. Three consecutive complete measurements with the same comparison identity establish two improvement rounds. An incomplete or incomparable sample breaks the sequence.

Two rounds below 5%, including regressions, flag an early review. Interpret the signal against measurement noise and the acceptance gap: profile the remaining bottleneck, revise the hypothesis, or change the approach. Give repeated experiments a concrete verification purpose. A recorded review consumes the current signal; another low-gain signal requires three new comparable samples. Review signals leave experiments authorized and acceptance unchanged.

When progress requires a goal or scope change, additional authorization, or resolution of a blocker you cannot remove, present the evidence and the specific decision needed. Continue unaffected work and keep unmet criteria open. Routine strategy changes and stage handoffs stay with the coordinator.

### User budgets and existing records

A hard time budget applies only when the user sets one. Start with `mode:bounded`, positive `limitMinutes`, and `source` containing the user's exact instruction; the coordinator verifies that the instruction establishes a limit. A review interval may exceed a short budget. At the limit, stop new experiments covered by that budget and present gains, gaps, and the next proposed action. Continue only work outside the limit's scope; an overall task limit also covers repair, review, and independent work.

`decide` records the user's `choice` and original `source`. `continue` requires positive `extensionMinutes` for a bounded phase; `autonomous` removes the time limit with the user's authorization; `phase` preserves a user-selected phase delivery. Keep measurements and decision history. Neither a review nor a repeated `start` renews a budget. A policy update does not resume a phase the user chose to stop, and authorization does not end an outstanding pause: record `decide` or `resume` as appropriate after resolving the reason.

Existing schema-version-1 records remain readable. The first budget event adds phase policy metadata while preserving timestamps, exclusions, measurements, events, and unrelated workflow state. A legacy phase with a recorded default start and no custom limit or user decision becomes autonomous. Other legacy phases return `decision:reconcile`: the coordinator reads saved instructions and records `policy` with `mode`, supporting `source`, and `limitMinutes` only for a genuine user budget. A numeric limit or an extension prompted by the old default gate alone does not establish a user-imposed cap. Use existing authorization to resolve the policy; ask only if a material ambiguity remains. Retain the legacy values and explicit phase-delivery choices. Reconcile stale waiting summaries with the resulting state; preserve actual user waits and external blocks until their reasons are resolved.

## Stage handoff

Use fresh implementation and review contexts at major stage boundaries by default. Keep independent work moving along the dependency graph. Retain the reviewer through the same issue's repair loop and defer handoff until it is resolved. The original owner completes or cancels active checks and confirms their state before handoff.

Pass a compact packet containing the target, stage, pinned commit, interface contracts, unresolved issues, and evidence index. Keep detailed logs and exploration history behind paths; the receiver independently decides what evidence is reusable. Save the packet with `workflow.py ... handoff --input <packet.json>`: `stage`, `target`, `commit`, `contracts`, `unresolved`, `evidence`, `activeChecks`, `implementer`, and `reviewer`. Evidence must exist and have recorded hashes; active checks block handoff. Final `stage:acceptance` requires `crossTicketReview:true`. The tool checks declarations and structure; actual agent independence requires separate evidence.

The coordinator alone maintains the shared run record. Send updates on completion, blockers, and interface changes; implementers report state changes once. Use an independent final context to review shared contracts and coverage gaps across tickets, following [integration review](integration-review.md).
