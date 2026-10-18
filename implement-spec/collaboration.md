# Collaboration and performance budgets

## Performance budgets

Create one shared `phaseId` when performance work starts and persist it outside the repository. Analysis, implementation, and experiments share that time window. The default budget is 45 minutes, with a checkpoint at 30 minutes; the user may override both before starting. Agent changes, parallel work, and context compaction preserve the budget. Exclude only explicit user waits and external blocks, recording their start, end, and reason.

Use `scripts/workflow.py --state <absolute-path> --run-id <run-id> budget --input <event.json>`. Each event includes `phaseId`, `event`, and the actual timestamp `at` with a timezone. `start` accepts `limitMinutes` and `checkpointMinutes`. `pause` uses reason `user-wait` or `external-block`; `resume` ends the pause. `status` reports elapsed time, the checkpoint or tradeoff decision, and whether new experiments are allowed. Each incoming agent queries the shared state first.

`measure` includes a positive `durationSeconds`, `completeEntry`, `comparisonKey`, and the original measurement `source`. Hold the complete entry point, source scope, model, environment, cache state, and concurrency conditions fixed. Three consecutive complete measurements with the same comparison identity establish two improvement rounds. An incomparable sample breaks the sequence; the time limit still applies.

At the checkpoint, report measured gains and remaining gaps. When the budget expires or both improvement rounds are below 5%, including regressions, stop new experiments. Present the sources, gains, remaining requirements, and reason for further investment; obtain an explicit choice to continue or phase delivery. `decide` records the user's exact statement as `source` and their `choice`; continuing requires an explicit `extensionMinutes`. Necessary repairs, review, and independent work remain available. Preserve the performance acceptance bar and leave the decision pending until the user answers.

## Stage handoff

Use fresh implementation and review contexts at major stage boundaries by default. Keep independent work moving along the dependency graph. Retain the reviewer through the same issue's repair loop and defer handoff until it is resolved. The original owner completes or cancels active checks and confirms their state before handoff.

Pass a compact packet containing the target, stage, pinned commit, interface contracts, unresolved issues, and evidence index. Keep detailed logs and exploration history behind paths; the receiver independently decides what evidence is reusable. Save the packet with `workflow.py ... handoff --input <packet.json>`: `stage`, `target`, `commit`, `contracts`, `unresolved`, `evidence`, `activeChecks`, `implementer`, and `reviewer`. Evidence must exist and have recorded hashes; active checks block handoff. Final `stage:acceptance` requires `crossTicketReview:true`. The tool checks declarations and structure; actual agent independence requires separate evidence.

The coordinator alone maintains the shared run record. Send updates on completion, blockers, and interface changes; implementers report state changes once. Use an independent final context to review shared contracts and coverage gaps across tickets, following [integration review](integration-review.md).
