# Stage handoff

Use fresh implementation and review contexts by default when moving from functional implementation to performance work or final acceptance. Retain the reviewer through the same issue's repair loop and defer handoff until it is resolved. Keep independent work moving along the dependency graph. The original owner completes or cancels active checks and confirms their actual state first.

Pass a compact handoff packet containing the target, stage, pinned commit, interface contracts, unresolved issues, and evidence index. Keep detailed logs and exploration history behind paths; the receiver independently assesses evidence reuse. Carry unresolved [stall records](progress.md) with their issues.

Save the packet with `workflow.py ... handoff --input <packet.json>`: `stage`, `target`, `commit`, `contracts`, `unresolved`, `evidence`, `activeChecks`, `implementer`, and `reviewer`. Evidence must exist and have recorded hashes; active checks block handoff. Final `stage:acceptance` requires `crossTicketReview:true`. The tool checks declarations and structure; actual agent independence requires separate evidence.

The coordinator alone maintains the shared run record. Implementers report each completion, blocker, or interface change once. Use an independent final context to review shared contracts and coverage gaps across tickets, following [integration review](integration-review.md).
