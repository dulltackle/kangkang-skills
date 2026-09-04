# Write-back — remote trackers

For repos whose `docs/agents/issue-tracker.md` configures **GitHub** or another external tracker.
The ticket lives outside the repo, so the commit lands first and the write-back follows it.

The ticket is the source of truth for state; the commit message records what each commit
delivered. Neither is generated from the other — the ticket body is edited in place, and
regenerating it from the commit message would drop everything else the ticket carries.

## The acceptance-criteria region

The region runs from the `## Acceptance criteria` heading to the next heading of the same level.
Match each criterion by its text within that region.

## GitHub

Re-read, flip, write back, comment:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only:  - [ ] …  →  - [x] …
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue comment <n> --body "<comment-template>"
```

## Other trackers

GitLab, Jira, Linear, or anything else the user described in their own words: follow the workflow
written in `docs/agents/issue-tracker.md`. Everything above still applies — the region, matching
by text, stopping on a mismatch, and the split-state report below.

Where that file does not say how to edit a ticket body, **stop and ask**. The command comes from
that file and nowhere else: a wrong write to somebody's tracker is worse than a run that stopped
and reported.

## On failure — report the split state

The commit has landed and stays landed. Report honestly: what landed, what did not, what is left
to do by hand. Give a paste-ready command and **keep the temp body file** — it is the most
expensive artefact of the run.

```
⚠ 已提交 abc1234，但 #42 的 body 写回失败（403）。ticket 未被修改。手动补：
  gh issue edit 42 --body-file "$TMPDIR/issue-42.md"
```

A **mismatch** lands here too: write nothing back and report it the same way.
