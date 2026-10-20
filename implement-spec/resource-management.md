# Run resources

Read when creating worktrees, starting preview services or long checks, resuming a run, or cleaning up after handoff. The coordinator records the registry's absolute path as `resourceRegistry` and a unique `runId` in `run.json`. Keep resource details in that registry. Each implementer registers its own resources; the coordinator reconciles them and reports the outcome.

## Create and register

Treat creation and registration as one step: save the creating interface's actual result, register the resource, and read it back. Proceed with handoff or replacement only after registration succeeds. If creation succeeds but registration fails, preserve the resource, result, and handle; repair registration rather than repeating creation.

For a worktree, record its creating interface, actual path, owner and ticket, purpose, stable identity, and creation evidence. Ordinary Git worktrees also need the repository path; app-managed worktrees retain the management tool's identity key. For a process, record its working directory, purpose, starting interface, host job or session handle, and an identity that distinguishes restarts. A PID alone cannot identify the original process. Creation evidence includes the command or tool call, successful result, time, and resource identity. Keep sensitive logs in controlled files rather than conversation output.

Use `scripts/resources.py` to maintain the registry. It uses the Python 3 standard library and POSIX `fcntl` for locking. Where this environment is unavailable, use an equivalent atomic host facility with the same fields and reconciliation procedure. The tool locks writes, replaces the registry atomically, and preserves creation evidence and subsequent events. Matching registrations can be retried; reconcile identity conflicts before registering a new resource under a new ID.

Replace `<skill-dir>` and `<run-dir>` with actual absolute paths and `<run-id>` with the recorded identity. See `--help` for arguments. When first constructing `register` or `record` input, or fixing input validation errors, read [resource input examples](resource-inputs.md).

Processes use `kind: process`, the actual management interface as `manager`, and a `handle` field. Their identity includes the host, job or session identity, and start time. Register a new identity when reusing a path or restarting a service. App-managed worktrees use their management interface and actual identity key rather than being treated as ordinary Git worktrees.

## Resume and observe

Read the registry and run `inspect`, then query actual resources through their original management interfaces. `inspect` checks evidence hashes, local paths, and ordinary Git worktree registration, HEAD, and whether changes exist. It does not inspect or stop processes. Historical events locate the last known state; current use still requires host observation. An empty process list in a sandbox does not prove that the actual host has no active users.

Save each observation's resource identity, time, presence, active use, host visibility, changes, and evidence. When host visibility is unverified, record `hostScope: unverified` and `activeUse: unknown`. Registration is complete when the read-back identity and evidence match. Resume reconciliation is complete when every resource has a current observation or an explicit reason its state is unknown.

For missing or changed evidence or mismatched records, consult the original interface and creation evidence; retain the resource until reconciled. Update only missing or changed records, preserving the original registration. For older runs without a registry, import entries supported by `run.json`, actual creation calls, or reliable host records. Similar names do not establish ownership; retain resources whose ownership remains unclear.

Use the same entry point for observations and cleanup results. Pass the saved raw result as `--evidence`; repeat `--recovery` to record recovery files and their actual SHA-256 values.

The tool validates fields, resource identity, and saved-file hashes. It does not establish the truth of an input report or prove that a backup is recoverable. Preserve the corresponding raw host result and verify backups or recovery commits under the existing acceptance requirements.

## Clean up individually

After successful handoff, the coordinator processes each registered resource:

1. Apply the [handoff and cleanup conditions](acceptance.md#4-clean-up-temporary-worktrees) to ownership, current use, and authorization. Inspect staged, unstaged, untracked, and ignored worktree content; preserve any ineligibility reported by the original management interface.
2. Save and verify recovery materials. Stop a process through its original host session or service interface only when its identity still matches, it is unused, and it belongs to this run's temporary work. Then process its worktree. Retain resources with uncertain identity or use and continue with other entries.
3. Clean up through the creating interface, using normal removal for ordinary Git worktrees. Respect management refusals without forced deletion or switching interfaces to bypass the refusal. A failed entry does not stop the rest of the list.
4. Query the actual host afterward. Record `type: cleanup` and `status: removed`, `stopped`, `retained`, or `failed`, with the reason, raw result, and recovery materials. `removed` and `stopped` require actual-host observation that the resource is absent and inactive; a submitted request alone is insufficient.

Finish when every entry has a current disposition or explicit retention reason. Summarize removed, stopped, retained, and failed resources separately from delivery status. On resume, query previously failed or retained resources before continuing. Reconcile completed operations rather than repeating unchanged cleanup.

## Capture original interface results

`resources.py ... capture --input <envelope.json>` saves an immutable original result, SHA-256, execution record, and applicable resource identity. It returns a summary and the original-result path. The envelope contains `id` (a unique safe filename), `owner`, `purpose`, `location`, `manager`, `operation`, `observedAt`, and `result` (the unmodified actual return object). Remove credentials at the log producer; exclude environment and authentication dumps.

Initial support covers Codex/Linux results from `manager:exec_command, operation:start`: an `exit_code` creates only a completed execution record; a `session_id` registers a managed process and handle. Observe the original session through `manager:write_stdin, operation:observe`, with `resourceId` and the original `handle`. Its exit code establishes only that host session's termination; verify descendants and formal jobs through their own interfaces. Failed queries or unrecognized interface results remain `unknown`. Local `subprocess.returncode` does not establish a host terminal state.

After creating an ordinary Git worktree, use `manager:git, operation:create` with its actual `location` and `repository`. Preserve the execution interface's original `exit_code`, `output`, and other result fields. The command queries actual Git registration and HEAD before recording the identity. App-managed worktrees and project formal jobs retain their established interfaces and register/record protocol.

`capture` records results rather than creating resources. If the original call succeeds but registration fails, preserve the input, original result, and handle; repair the bookkeeping and retry the same input. Keep the saved original even if later field validation fails. Read legacy `schemaVersion:1` registries compatibly and reconcile entries as needed. `inspect` preserves old unknown states; preserve historical records and establish actual resource presence separately from registry contents.
