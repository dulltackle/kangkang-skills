# Stalled progress

Read when the entry point's stall or external-blocker conditions fire. This protocol covers discovery, implementation, review fixes, performance, acceptance, and cleanup. Each stage's existing gates still apply.

## Recognize and report

An attempt tests a hypothesis or changed condition and observes the result; a status poll is not an attempt. New evidence rules out a hypothesis, narrows the cause, or verifies a fix. Rewording the plan, recording a `review`, or repeating a command alone does not establish progress. Use the existing waiting protocol for healthy long checks; report confirmed failure, lost contact, or an external dependency block as observed.

Before the next attempt, give the user a compact report:

- **Problem and impact:** what is stuck, which tickets and subsequent actions it affects.
- **Attempts and evidence:** hypotheses ruled out, key results, and original evidence paths.
- **Next action:** what will change and what it tests; when a user decision is needed, state the specific choice and recommendation.

Continue autonomously when a new direction can be tested. If progress requires a goal or scope change, additional authorization, or human intervention, pause affected paths and request that decision. Continue independent work allowed by existing gates. The two-attempt threshold triggers a report, not a stop or authorization renewal. Honor explicit user budgets.

## Preserve and deduplicate

The coordinator keeps the problem identity, ruled-out hypotheses, last substantive progress, reporting status, and next action or pending decision in the run record's blocker entry. Implementers promptly report stalls to the coordinator, who informs the user. Preserve unresolved problems across reviews, agent changes, context compaction, and handoffs.

Before a run record exists, save the same minimal record and evidence outside the repository and report its path. Incorporate it into the blocker entry when the run record is created, preserving original sources. Report promptly while preparing the record.

Reuse the existing summary while a blocker is unchanged. Maintain host-required updates without repeating decision requests or polling merely to generate an update. Update the record and inform the user when new evidence arrives, impact changes, the planned action is ruled out, a new decision is needed, or the blocker clears. If no justified next action remains, state the unresolved blocker and the help needed; keep unmet criteria open.

A report is complete when the user has received the impact and next action, the record supports recovery, and affected paths follow their stage's continuation or pause rules. Script records and counters do not replace technical judgment, acceptance, or actual-host observations.
