# Branches, run records, and authorization

Verify and record the baseline; deliver on one integration branch. Preserve existing staging and unrelated work, using a separate worktree when isolation is needed. On resume, reconcile the record with the actual branch, tracker, and resources before reusing work.

Create a persistent `run.json` outside the repository and report its absolute path. Update it after reviews, merges, user confirmations, and tracker writes:

- Baseline and integration commits; each ticket's branch, worktree, status, and blockers.
- Absolute `resourceRegistry` path and unique `runId`; keep resource details in that registry.
- Reviewer, baseline and target, files, diffs, rules, findings and dispositions, correspondence to the integration diff, and criterion evidence with its applicable commit.
- Exact user confirmations, their content and scope, and completed or pending tracker operations.
- Discovery query scope, sources, pagination and access status, included, excluded, and unresolved relationships, dependency graph, and per-ticket implementation, review, acceptance, and write-back state. Preserve raw queries before adding them to the record.

Read [run resources](resource-management.md) before creating worktrees, preview services, or long checks. Save successful results, register them, and read them back immediately. Before reuse on resume, query the original host interface. Resource reconciliation and task discovery remain separate requirements.

Open a draft PR after the first merge, marked as closing the spec and tickets with the configured ticket references. Readiness and closure follow [acceptance](acceptance.md).

Necessary configuration changes within the spec are authorized implementation work. Preserve recoverable originals or exact diffs before editing; record the target, affected scope, and completion evidence. On resume, reconcile authorization with actual state and continue when content and impact are materially unchanged. Added costs, broader permissions, unrelated configuration, or discarding user content require a user decision. Identify the specific authorization gap while continuing independent preparation. Respect host approval; preserve work and record a refusal's action and reason rather than changing routes to bypass it.
