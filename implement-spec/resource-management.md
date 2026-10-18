# Run resources

Read when creating worktrees, starting preview services or long checks, resuming a run, or cleaning up after handoff. The coordinator records the registry's absolute path as `resourceRegistry` and a unique `runId` in `run.json`. Keep resource details in that registry. Each implementer registers its own resources; the coordinator reconciles them and reports the outcome.

## Create and register

Treat creation and registration as one step: save the creating interface's actual result, register the resource, and read it back. Proceed with handoff or replacement only after registration succeeds. If creation succeeds but registration fails, preserve the resource, result, and handle; repair registration rather than repeating creation.

For a worktree, record its creating interface, actual path, owner and ticket, purpose, stable identity, and creation evidence. Ordinary Git worktrees also need the repository path; app-managed worktrees retain the management tool's identity key. For a process, record its working directory, purpose, starting interface, host job or session handle, and an identity that distinguishes restarts. A PID alone cannot identify the original process. Creation evidence includes the command or tool call, successful result, time, and resource identity. Keep sensitive logs in controlled files rather than conversation output.

Use `scripts/resources.py` to maintain the registry. It uses the Python 3 standard library and POSIX `fcntl` for locking. Where this environment is unavailable, use an equivalent atomic host facility with the same fields and reconciliation procedure. The tool locks writes, replaces the registry atomically, and preserves creation evidence and subsequent events. Matching registrations can be retried; reconcile identity conflicts before registering a new resource under a new ID.

Replace `<skill-dir>` and `<run-dir>` with actual absolute paths and `<run-id>` with the recorded identity. See `--help` for command arguments; input examples follow.

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

Processes use `kind: process`, the actual management interface as `manager`, and a `handle` field. Their identity includes the host, job or session identity, and start time. Register a new identity when reusing a path or restarting a service. App-managed worktrees use their management interface and actual identity key rather than being treated as ordinary Git worktrees.

## Resume and observe

Read the registry and run `inspect`, then query actual resources through their original management interfaces. `inspect` checks evidence hashes, local paths, and ordinary Git worktree registration, HEAD, and whether changes exist. It does not inspect or stop processes. Historical events locate the last known state; current use still requires host observation. An empty process list in a sandbox does not prove that the actual host has no active users.

Save each observation's resource identity, time, presence, active use, host visibility, changes, and evidence. When host visibility is unverified, record `hostScope: unverified` and `activeUse: unknown`. Registration is complete when the read-back identity and evidence match. Resume reconciliation is complete when every resource has a current observation or an explicit reason its state is unknown.

For missing or changed evidence or mismatched records, consult the original interface and creation evidence; retain the resource until reconciled. Update only missing or changed records, preserving the original registration. For older runs without a registry, import entries supported by `run.json`, actual creation calls, or reliable host records. Similar names do not establish ownership; retain resources whose ownership remains unclear.

Use the same entry point for observations and cleanup results. Pass the saved raw result as `--evidence`; repeat `--recovery` to record recovery files and their actual SHA-256 values.

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

The tool validates fields, resource identity, and saved-file hashes. It does not establish the truth of an input report or prove that a backup is recoverable. Preserve the corresponding raw host result and verify backups or recovery commits under the existing acceptance requirements.

## Clean up individually

After successful handoff, the coordinator processes each registered resource:

1. Apply the [handoff and cleanup conditions](acceptance.md#4-clean-up-temporary-worktrees) to ownership, current use, and authorization. Inspect staged, unstaged, untracked, and ignored worktree content; preserve any ineligibility reported by the original management interface.
2. Save and verify recovery materials. Stop a process through its original host session or service interface only when its identity still matches, it is unused, and it belongs to this run's temporary work. Then process its worktree. Retain resources with uncertain identity or use and continue with other entries.
3. Clean up through the creating interface, using normal removal for ordinary Git worktrees. Respect management refusals without forced deletion or switching interfaces to bypass the refusal. A failed entry does not stop the rest of the list.
4. Query the actual host afterward. Record `type: cleanup` and `status: removed`, `stopped`, `retained`, or `failed`, with the reason, raw result, and recovery materials. `removed` and `stopped` require actual-host observation that the resource is absent and inactive; a submitted request alone is insufficient.

Finish when every entry has a current disposition or explicit retention reason. Summarize removed, stopped, retained, and failed resources separately from delivery status. On resume, query previously failed or retained resources before continuing. Reconcile completed operations rather than repeating unchanged cleanup.

## Verify the tool

```sh
python3 <skill-dir>/evals/test_resources.py -v
```

Tests use temporary directories and Git repositories, without connecting to actual run resources, hosts, or trackers. Scenarios O–Q in `evals/scenarios.md` evaluate agent decisions separately; tool tests do not replace behavioral evaluation.

## 原接口结果自动登记

`resources.py ... capture --input <调用信封.json>` 自动保存不可覆盖的原件、SHA256、执行记录及适用的资源身份；默认返回摘要和原件路径。信封含 id（唯一安全文件名）、owner、purpose、location、manager、operation、observedAt、result（未经改写的真实返回对象）。日志先在生产端剔除凭据，不传环境/认证原文。

首轮支持 `manager:exec_command, operation:start` 的 Codex/Linux 返回：exit_code 只形成已结束执行记录，session_id 则登记持续 process/handle。后续实际 `write_stdin` 查询用 manager:write_stdin、operation:observe，带 resourceId 和原 handle；退出码只证明该宿主会话结束，全部后代和正式任务仍按原接口各自核对。查询失败或未知接口结果保持 unknown，本地 subprocess.returncode 不建立宿主终态。

普通 Git worktree 创建后用 manager:git、operation:create，location/repository 保存实际目标路径，result 保留原执行接口的 exit_code/output 等实际返回对象；入口实际查询 Git 登记及 HEAD 后登记身份。应用管理工作树及项目正式任务继续原入口，沿用 register/record 协议，不发明通用进程管理器。

capture 不执行资源创建。原始调用成功而登记失败时，保留输入/原结果和句柄，排除登记故障后原输入重试，不能重启命令或新建替代资源。原件写盘之后其他字段失败也保留文件。旧 schemaVersion:1 登记表兼容，只按实际使用核对；inspect 输出旧未知，绝不批量重写历史或据空表断言无资源。
