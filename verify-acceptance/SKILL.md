---
name: verify-acceptance
description: "Verify a ticket's acceptance criteria against the current commit and tick the earned ones on the ticket. Use when delivering ticket work, when the user asks whether a ticket's criteria pass, or wants acceptance written back to an issue."
---

# Verify Acceptance

Check each acceptance criterion of a ticket against the current commit, then record the earned ones on the ticket itself.

An `[x]` is a claim that somebody checked, and a wrong one is a lie that sits on the ticket forever. So every tick this skill writes is **earned**: you ran something and watched it pass, or the user gave their word on something you could only read. **When in doubt, don't tick, and say why.**

This skill never commits, pushes, opens a PR, or closes or reopens a ticket. It runs against work that is already committed; on a local tracker the caller commits the ticket edits.

## Which tracker

Read `docs/agents/issue-tracker.md`, then only the write-back file it points to. If the file is missing, tell the user to run `/setup-matt-pocock-skills`.

- **GitHub or another external tracker** → [write-back-remote.md](write-back-remote.md)
- **Local markdown** → [write-back-local.md](write-back-local.md)

Each file defines the **acceptance-criteria region** for its tracker and how to write to it.

## Process

### 1. Read the criteria

Re-read the ticket from the tracker, never from your context: it may have been edited since. Take the boxes inside the region. Every box outside it (task lists, sub-issue lists, hand-written todos) is out of scope.

**A ticket with no region** (hand-filed issues often have none): tick nothing and say so plainly, `#42 has no acceptance criteria region, nothing written back`. The criteria are the ticket's, never yours: writing your own is setting your own exam, sitting it, and marking it.

### 2. Verify and classify

Walk every criterion, those already `[x]` included. Each is one of these:

- **`ran`**: you executed something on the current commit and watched it pass: a test, the actual behaviour. Earned, so you tick it in step 3.
- **`read`**: a judgement only reading code or docs can make. Earned by the user's word alone, so it waits for step 4.
- **Unverified**: executable, but not run, failed, or blocked (a missing entry point, an unreachable host, an unmet precondition, or something that does not exist yet, such as the PR's own CI). It stays `[ ]`. The user's word never replaces an execution, so keep `read` for pure reading judgements.

Before calling a criterion blocked, probe its entry point with the tools you have: the command exists, the host answers, you hold the permission. A tool name or an installed file is not proof the current host can call it. Report a blocker as what is missing and how to restore it, then carry on with the rest.

Every `ran` and `read` carries one line of evidence: which test, what you did, which file you read.

**Regressions.** A criterion already `[x]` that now fails loses its tick, loudly: `⚠ #42 "POST /items returns 201" passed last run, items.test.ts fails on this run, unticked`. Moving the ticket backwards is right; leaving a tick that stopped being true is not. A closed ticket stays closed: untick, comment, and report it. Reopening is the user's call.

Criteria the user already confirmed keep their tick while the content they judged is unchanged: those are asked once, not every run.

### 3. Write back the `ran` ticks

1. **Re-read the ticket body** and align against *that* copy. A stale whole-body overwrite clobbers whoever edited it in between.
2. **Flip only boxes inside the region.** Tick the `ran` criteria; untick the regressions.
3. **Match by exact text, and a mismatch stops the run.** A criterion you did not verify stays `[ ]` and is reported. Something you verified with no matching criterion: **stop, write nothing back, and tell the user.** Fuzzy-matching fires exactly when a human edited the ticket, the case you least want a model guessing at.
4. **Append a comment** from the template below. The body is mutable state; the comment log is the only append-only record, and the only place an untick leaves a trace.

**A re-run that changes nothing writes nothing**: no body edit when no box flips, and no comment unless a box flipped or a `read` criterion now awaits confirmation. Callers re-verify on every run, and a comment per run buries the ones that matter.

**On failure, stop.** These writes fail on permissions, a deleted ticket, or a concurrent edit, and a retry produces the same error later. Every write runs or the run stops: a ticket that got commented but not updated contradicts itself. Your tracker's file gives the wording.

### 4. Ask about the `read` criteria

Only when unconfirmed `read` criteria exist; otherwise skip to step 6. Ask one question from the template, listing each criterion with what you read. Ask about the criteria and nothing else. Blocked executable criteria are reported as blockers, never put to the user for confirmation.

### 5. Write back the confirmations

Only after the user has answered, and only for the criteria they confirmed: their word is what earns those. Same four rules as step 3, with the confirmation comment. A declined criterion stays `[ ]`; the comment records the decline, and a later run asks again.

### 6. Report

The ticks earned this run, and every criterion still `[ ]` with why.

## Templates

Write the comment, the question, and the report in the language the user's instructions or the repo's history use. The templates fix the structure, not the language.

First comment. Omit any line that does not apply:

<comment-template>
abc1234 (feat/items)

Verified by running: POST /items returns 201 and persists; list page shows a skeleton
Unticked on regression: concurrent writes lose no orders (passed last run, items.test.ts fails on this run)
Awaiting confirmation: README updated; naming matches the glossary
</comment-template>

The question:

<question-template>
These 2 criteria were only read, not run, and are not ticked yet:
  · README updated               (read the "Install" section of README.md)
  · Naming matches the glossary  (uses Item / Batch from GLOSSARY.md)

Do you accept them?
</question-template>

Confirmation comment:

<confirmation-template>
Confirmed by the user: README updated
Declined by the user: naming matches the glossary
</confirmation-template>

Omit either line when it does not apply.

A local-markdown tracker varies the first comment slightly: see its file.
