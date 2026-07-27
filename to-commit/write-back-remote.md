# Write-back — remote trackers

For repos whose `docs/agents/issue-tracker.md` configures **GitHub**, **GitLab**, or some **other**
external tracker. The ticket lives outside the repo, so the commit lands first and the write-back
follows it.

The ticket is the source of truth for state; the commit message records what each commit
delivered. They carry different things and neither is generated from the other.

## The acceptance-criteria region

The region runs from the `## Acceptance criteria` heading to the next heading of the same level.
Match each criterion by its text within that region.

**Never regenerate the body from the commit message** — that would drop everything else the ticket
carries.

## GitHub

Re-read, flip, write back, comment:

```bash
gh issue view <n> --json body --jq .body > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only:  - [ ] …  →  - [x] …
gh issue edit <n> --body-file "$TMPDIR/issue-<n>.md"
gh issue comment <n> --body "<comment-template>"
```

## GitLab

Same shape with `glab`:

```bash
glab issue view <n> -F json | jq -r .description > "$TMPDIR/issue-<n>.md"
# edit that file, inside the `## Acceptance criteria` region only
glab issue update <n> --description "$(cat "$TMPDIR/issue-<n>.md")"
glab issue note <n> --message "<comment-template>"
```

## Other trackers

Jira, Linear, or anything else the user described in their own words: follow the workflow written
in `docs/agents/issue-tracker.md`. Everything above still applies — the region, matching by text,
stopping on a mismatch, and the split-state report below.

If that file does not say how to edit a ticket body, **stop and ask**. Do not guess at an API or a
CLI: a wrong write to somebody's tracker is worse than a run that stopped and reported.

## On failure — report the split state

The commit has already landed. It cannot be unmade, so report honestly: what landed, what did not,
what is left to do by hand. Give a paste-ready command and **keep the temp body file** — it is the
most expensive artefact of the run.

```
⚠ 已提交 abc1234，但 #42 的 body 写回失败（403）。ticket 未被修改。手动补：
  gh issue edit 42 --body-file "$TMPDIR/issue-42.md"
```

The same applies to a **mismatch**: something you verified with no matching criterion on the
ticket. Write nothing back and report it the same way.

Never try to undo the commit to make the two halves match again.
