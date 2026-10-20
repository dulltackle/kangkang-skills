# Resource input examples

Read when first constructing `register` or `record` input, or fixing validation errors. Follow [run resources](resource-management.md) for placeholders and operating rules.

## Register and read back

```sh
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> register --input <run-dir>/resource.json --evidence <run-dir>/creation-result.json
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> inspect
```

Registration input:

```json
{
  "id": "ticket-43-worktree",
  "kind": "worktree",
  "owner": "implementer-A / demo#43",
  "purpose": "Implement ticket 43",
  "manager": "git",
  "identity": "demo-run-42 / git-worktree / /absolute/worktree-43",
  "location": "/absolute/worktree-43",
  "repository": "/absolute/repository"
}
```

## Observation and cleanup events

```sh
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> record --input <run-dir>/observation.json --evidence <run-dir>/host-result.json
```

Event input:

```json
{
  "resourceId": "ticket-43-worktree",
  "identity": "demo-run-42 / git-worktree / /absolute/worktree-43",
  "type": "observation",
  "observedAt": "2026-10-13T00:00:00Z",
  "hostScope": "actual-host",
  "presence": "present",
  "activeUse": "active",
  "reason": "A preview job on the actual host still uses this directory"
}
```

