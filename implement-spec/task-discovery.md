# Task discovery and reconciliation

Run before initial implementation, on resume, before final acceptance, and before handoff actions. The coordinator establishes the complete ticket set, saves a verifiable discovery snapshot, and uses it for scheduling and acceptance.

## Discover the ticket set

Read the repository's tracker conventions to establish repository or project boundaries and the formats for parent links and dependencies. Query open and closed tickets within that scope, combining:

- Native parent-child relationships.
- Child tickets explicitly listed in the spec body.
- Explicit parent links in other ticket bodies pointing back to this spec or an already discovered child.

Deduplicate by tracker, repository or project, and ticket ID. Recursively discover explicit descendants and resolve dependencies. Resolve cross-repository links by full identity so matching numbers remain distinct tickets. Read dependency targets to determine readiness; a dependency alone does not establish parentage.

Search for numbers or links to find candidates, then read their bodies to verify relationships. Background mentions, examples, ordinary references, and dependency links alone do not establish parentage. Include explicit relationships automatically. For conflicting or ambiguous parentage, record the original text, source, and decision needed; ask the user and pause affected tickets and their dependents. Other paths may proceed once queries are complete and their independence is verified.

For every source, record query scope, filters, pagination completion evidence, and results. A fixed result cap or one empty page does not establish completeness. Resolve truncation or indexing limits through verifiable alternatives, such as fully paginated listings and body reads. If the tracker genuinely lacks a native relationship type, record that fact and use the remaining applicable sources. Distinguish unsupported features from access failures and API errors.

## Failure and recovery

Before the first complete snapshot, API failure, incomplete pagination, insufficient access, or unverifiable coverage stops implementation. Continue query recovery, read-only investigation, and evidence preservation. An unknown ticket set remains unknown.

After a complete snapshot exists, query failure permits local development and tests only for tickets already assigned in that snapshot with satisfied dependencies. Pause new dispatch, integration, acceptance write-back, and delivery. Preserve the failure source, time, and scope. Restore complete queries, reconcile additions, removals, criterion changes, and dependencies, then reassess affected work before proceeding.

After context compaction with unchanged external state, read the existing complete snapshot, run record, and necessary updates. On a resume where external state may have changed, reconcile resources and tracker state first. After initial discovery, incremental reconciliation is valid only with evidence covering the full scope: preserve the baseline, cursor and pagination, deletions, and relationship changes. A single page or unverified updated-time filter is insufficient. The current tools have no incremental tracker client; use complete queries when coverage cannot be proven. Always perform complete reconciliation before delivery.

Use `workflow.py --state <path> --run-id <run-id> discovery --input <event.json>` to record gates. An initial `failed` event leaves no local tickets eligible. After a full `snapshot`, `failed` preserves only the snapshot's assigned `localTickets`. A restored snapshot reports `changedTickets`; reconcile each with `reconciled` before integration resumes. `continuation` reuses the snapshot, but write-back and delivery still require fresh complete reconciliation. When external state may have changed, first use `gate` with `purpose:resume` to revoke old query eligibility, then restore a full snapshot and reconcile changes. After the final full snapshot, query `gate` with `purpose:handoff`.

A snapshot contains `scope`, `tickets` (ticket-to-criteria/relationship content identities), `assigned`, `mode:full`, and three complete `sources`: `native`, `bodies`, and `dependencies`, each with an evidence path. The tool checks declared correspondence. The coordinator verifies original pagination and actual relationships, including the parent ticket.

The **discovery snapshot** contains the parent spec's identity, query time and scope, completeness evidence for each source, deduplicated tickets, relationship evidence for each ticket, dependencies, excluded candidates with reasons, and unresolved relationships. Unresolved relationships block affected paths and full-spec handoff; they do not trigger the global stop reserved for query failures.

## Reconcile and recover

On resume, reconcile existing resources through [run resources](resource-management.md), then complete task discovery and reconciliation below. Resource observations govern reuse and cleanup; they do not change query-completeness requirements.

Compare the new snapshot with the run record. Identify added, previously missed, removed, or changed relationships and dependencies. When a ticket disappears, verify whether its parentage changed or a query failed before removing it from the acceptance set, and record the reason. Handle ambiguity and query failures under the rules above.

For each added or previously missed ticket, reconcile current acceptance criteria, matching commits, review coverage, execution evidence, still-applicable user confirmations, and tracker write-back state. Parent acceptance, a closed ticket, or apparently sufficient code cannot replace ticket-level verification. Complete missing implementation and review before final acceptance. Recompute the frontier when tickets or dependencies change.

Preserve commit history and recoverable work. Map each ticket to existing commits rather than redoing delivered code to reconstruct one branch or commit per ticket. Use new commits referencing affected tickets for missing implementation and final fixes. Reuse evidence only when it matches current criteria and unchanged content; final executable acceptance still follows the evidence-validity rules in [acceptance and handoff](acceptance.md).

Keep full-spec handoff pending while reconciliation, relationships, or any ticket's implementation, review, acceptance, or write-back evidence remains unresolved. If the parent is already closed or the PR is ready, record the actual state and correct it under tracker rules and existing authorization. Report blockers when additional permission is needed; distinguish a planned correction from a completed one.
