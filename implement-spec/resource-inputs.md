# 资源输入样例

仅在首次构造 `register` / `record` 输入或修复校验错误时读取。占位符与行为约束见[资源协议](resource-management.md)。

## 注册与读回

```sh
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> register --input <run-dir>/resource.json --evidence <run-dir>/creation-result.json
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> inspect
```

注册输入：

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

## 观察与清理事件

```sh
python3 <skill-dir>/scripts/resources.py --registry <run-dir>/resources.json --run-id <run-id> record --input <run-dir>/observation.json --evidence <run-dir>/host-result.json
```

事件输入：

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

