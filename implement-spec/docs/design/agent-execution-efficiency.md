# Agent execution cost design

Status: Q1-Q14 and the overall design are confirmed. The later autonomy revision below supersedes the original Q2/Q4 time and low-gain gates; other decisions retain their scope. The spec is published as [ClapGrid #158](https://github.com/dulltackle/ClapGrid/issues/158) with `ready-for-agent`. Skill, tool, and project-check changes have been implemented in the confirmed order. CLI and behavioral regressions have run; cost benefits remain a pilot. Consult #158 and the delivery record for final-commit acceptance and actual CI status.

## Scope

Use the ClapGrid #148 retrospective to reduce repeated reading, coordination, and resource-bookkeeping costs while limiting deterioration in actual execution time. Record uncached input tokens, output tokens, model calls, and actual execution time separately; list cached input separately. Compare the same task and acceptance coverage. Establish the baseline before fixing improvement targets.

The user-designated maintained source for generic skill and tool changes is defined in [maintenance](../../maintenance.md). `/home/forclaw/.skills-manager/skills/implement-spec/` is the installed copy; its Git ownership does not identify the maintained source. ClapGrid fixture, CI, and verification-document changes belong to `dulltackle/ClapGrid`.

## Confirmed implementation order

1. S1: performance investment decisions; S2: multi-agent stage handoff; T1: execution and resource-registration automation.
2. P1: formal-environment preflight; S3: task discovery and recovery; T2: acceptance evidence summaries.
3. P2: CI duration and duplicate runs; D1: on-demand documentation.

Existing performance acceptance remains tracked in ClapGrid #148, #150, #151, and #156 at its original bar.

## First confirmation

The user answered "Use all recommendations" (translated), confirming:

- **Q1:** Prioritize eliminating repeated model overhead while limiting deterioration in actual execution time. Present metrics separately; cumulative cached input is not actual cost.
- **Q2 (superseded by the autonomy revision):** When the performance budget expires, stop new experiments and present measured gains, remaining gaps, and the reason for further investment. Let the user choose continued investigation or phased delivery. Continue necessary repairs, review, and independent work introduced so far; keep unmet criteria open.
- **Q3:** Retain the original reviewer through the same issue's repair loop; allow a fresh agent after a stage completes. Pass the target, pinned commit, interface contracts, unresolved issues, and verifiable review and execution evidence. The original owner closes out active checks first; the incoming agent independently decides what conclusions are reusable.

## Verified tool boundaries

`implement-spec/scripts/resources.py` provides atomic registration, identity-conflict checks, evidence hashes, observations, and cleanup records. Command execution, host process queries and termination, and verification of declared terminal states remain with their original interfaces and evidence.

Local Python can record the return code of a child it starts and waits for. That return code does not establish termination of the outer tool session or every background descendant. T1 retains the original management identity and actual interface result; unqueryable state remains explicitly unknown.

## Second confirmation

The user answered "Use all recommendations" (translated), confirming:

- **Q4 (superseded by the autonomy revision):** Default performance budget: 45 minutes, with a gain checkpoint at 30 minutes. Include analysis, implementation, and experiments. Parallel agents share the budget; changing agents preserves it. Exclude user waits and explicit external blocks. Two consecutive comparable complete-entry improvements below 5% trigger an earlier tradeoff decision, separate from formal performance acceptance. The user may override defaults before starting.
- **Q5:** Use fresh implementation and review contexts when moving from functional implementation to performance work and then final acceptance. Retain the reviewer through the same issue's repair loop; defer handoff until resolution. Pass a compact summary and evidence index, with detailed history available on demand. The coordinator maintains shared state; final review emphasizes cross-ticket interactions and coverage gaps.
- **Q6:** T1 initially supports current Codex/Linux execution sessions and ordinary Git worktrees: save original interface results, register identities, append observations, and generate summaries. Project formal jobs use established entry points. Preserve unknown terminal states. Cross-host support, other platforms, and a new process-management mechanism are outside the first iteration.

## Third confirmation

The user answered "Use all recommendations" (translated), confirming:

- **Q7:** Keep execution records for short synchronous commands. Register active sessions, background checks, services, formal jobs, and worktrees as managed resources. Read legacy registries compatibly and reconcile them as operations require; retain historical evidence and existing unknown states.
- **Q8:** P1 standardizes writable-cache isolation in watch fixtures within the existing preflight chain. Run formal-environment-sensitive files early and count their original evidence in the existing same-run cumulative coverage. Reuse test entry points and cumulative machinery rather than adding duplicate full preflight runs.
- **Q9:** Stop implementation until first discovery is complete. After a complete snapshot exists, query failure permits assigned local development and tests while pausing new dispatch, integration, and acceptance write-back. Restore queries, reconcile scope changes, and reassess affected work before advancing.
- **Q10:** T2 initially generalizes existing mechanical checks into evidence summaries, gaps, and proposed write-back plans. Reviewers make semantic judgments; remote write-back follows established authorization. Material completeness alone does not earn acceptance. Reuse the tracker client.

## Fourth confirmation and source correction

The user accepted the recommendations for Q11 and Q13. For Q12, the user specified the true maintained source recorded in [maintenance](../../maintenance.md), accepting the remaining scope recommendations.

- **Q11:** Preserve push, PR, and manual triggers. Push defaults to the branch tip; PR defaults to the merge result, so they represent distinct coverage. First handle replacement of automatic runs within the same workflow, event, and ref. Isolate manual triggers and reruns so an old-commit rerun does not displace a newer check. Record cancellation as cancellation, never passing. Measure duration and job-timeout margin.
- **Q12:** Limit documentation work to the maintained implement-spec entry point and references, plus ClapGrid verification guidance. Keep steps and conditional pointers in the main document and disclose protocol details on demand. Tools return summaries and original-evidence paths by default. Keep global `AGENTS.md` concise; other skills are outside scope.
- **Q13:** Evaluate at two levels. Deterministic checks cover shared budgets across agents, handoff evidence, registration failure, lost sessions, offline recovery, missing evidence, and retention during cleanup. Under the same model and environment, compare original and candidate versions on a few fixed normal-delivery, low-gain, and interruption scenarios. Report tokens, calls, and actual duration separately. Historical logs are diagnostic evidence rather than a fair baseline. Establish the baseline before fixing targets. Roll out only with complete coverage and repeatable gains; unproven benefits remain a pilot.

At source correction, the maintained directory had no Git repository or publication/synchronization instructions. Five key files (the entry point, discovery, resource and acceptance documents, and resource script) matched the installed copy byte for byte; that did not establish automatic synchronization. The three design documents were moved back to the maintained source. Their former location has an automatic backup commit; preserve that history and the source's non-Git state.

## Final confirmation and spec publication

Through `to-spec`, the user confirmed the overall design (Q14): edit and verify the maintained source, then explicitly synchronize to the installed copy after evaluation, retaining the old version and checking hashes. The maintained source remains authoritative. Preserve its non-Git state and inspect actual installation management and affected files before synchronization.

The full spec was published as [ClapGrid #158](https://github.com/dulltackle/ClapGrid/issues/158); its body and `ready-for-agent` label were read back. Implementation entered verification and delivery. Acceptance ticks continue to require actual evidence on #158.

## Autonomy revision

The user subsequently requested autonomous completion, with questions reserved for goal or scope changes, additional authorization, and blockers the agent cannot remove. This supersedes Q2 and Q4's default stop-and-renew policy. [Performance work](../../performance.md) is authoritative: periodic and low-gain reviews guide the agent's next action; only user-set budgets gate further experiments. Acceptance requirements remain unchanged.

Q13's deterministic coverage now includes recurring review acknowledgment, continuation beyond the former default limit, explicit user budgets, evidence-preserving legacy migration, and preservation of user-selected phase delivery. Behavioral scenarios test these decisions separately from cost-benefit claims. This change establishes the requested execution policy; token, duration, and end-to-end delivery benefits still require measured evidence.

## Evidence

- Retrospective metrics and original-session index: `/home/forclaw/tmp/clapgrid-148-retro/metrics.json`.
- Structured interview record: `/home/forclaw/tmp/agent-efficiency-design/design-state.json`.
- Resource constraints: [run resources](../../resource-management.md); registration tool: [resources.py](../../scripts/resources.py).

[Glossary](../../GLOSSARY.md) | [Responsibility-boundary ADR](../adr/0001-execution-evidence-and-acceptance-boundaries.md)
