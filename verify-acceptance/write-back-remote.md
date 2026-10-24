# Write-back: remote trackers

For repos whose `docs/agents/issue-tracker.md` configures **GitHub** or another external tracker. The ticket lives outside the repo, so its edits never go into a commit.

The ticket is the source of truth for state; a commit message records what one commit delivered. Neither is generated from the other: the ticket body is edited in place, and regenerating it from a commit message would drop everything else the ticket carries.

## The acceptance-criteria region

The region runs from an **acceptance heading** to the next heading of the same level. An acceptance heading is a level-2 heading (`##`) whose text, trimmed, is one of:

- `Acceptance criteria`, in any letter case
- `验收标准`
- `验收条件`

The list is closed. Nothing else is a region: not another wording (`## 验收`, `## Acceptance criteria:`), not a deeper heading (`### 验收标准`), not prose that reads like criteria, not a comment. The heading is read as it stands; never rename it.

**Two acceptance headings** in one body is a mismatch: there is no telling which one is the ticket's. Stop as soon as you find them, before verifying anything: run no criterion, write nothing back, and report where each sits.

A ticket with no region gets the candidate scan, which reads the comments too:

```bash
gh issue view <n> --json body,comments
```

## GitHub

Re-read, flip, write back, comment:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file, inside the region only:  - [ ] …  →  - [x] …
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue comment <n> --body "<comment-template>"
```

Never `gh issue close` or `gh issue reopen` here: the ticket's open or closed state belongs to the PR that closes it.

## Other trackers

GitLab, Jira, Linear, or anything else the user described in their own words: follow the workflow written in `docs/agents/issue-tracker.md`. Everything above still applies: the region, matching by text, stopping on a mismatch, and the split-state report below.

Where that file does not say how to edit a ticket body, **stop and ask**. The command comes from that file and nowhere else: a wrong write to somebody's tracker is worse than a run that stopped and reported.

## On failure: report the split state

Whatever landed before the failure stays landed. Report honestly what landed, what did not, and what is left to do by hand. Give a paste-ready command and **keep the temp body file**: it is the most expensive artefact of the run.

```
⚠ abc1234 is committed, but writing #42's body failed (403). The ticket is unchanged. To finish by hand:
  gh issue edit 42 --body-file "$TMPDIR/issue-42.md"
```

A **mismatch** lands here too: write nothing back and report it the same way.
