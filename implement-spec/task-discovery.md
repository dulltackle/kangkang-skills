# Task discovery and reconciliation

Run before initial implementation, on resume, before final acceptance, and before handoff actions. The coordinator establishes the complete ticket set, saves a verifiable discovery snapshot, and uses it for scheduling and acceptance.

## Discover the ticket set

Read the repository's tracker conventions to establish repository or project boundaries and the formats for parent links and dependencies. Query open and closed tickets within that scope, combining:

- Native parent-child relationships.
- Child tickets explicitly listed in the spec body.
- Explicit parent links in other ticket bodies pointing back to this spec or an already discovered child.

Deduplicate by tracker, repository or project, and ticket ID. Recursively discover explicit descendants and resolve dependencies. Resolve cross-repository links by full identity so matching numbers remain distinct tickets. Read dependency targets to determine readiness; a dependency alone does not establish parentage.

Search for numbers or links to find candidates, then read their bodies to verify relationships. Background mentions, examples, ordinary references, and dependency links alone do not establish parentage. Include explicit relationships automatically. For conflicting or ambiguous parentage, record the original text, source, and decision needed; ask the user and pause affected tickets and their dependents. Other paths may proceed once queries are complete and their independence is verified.

For every source, record query scope, filters, pagination completion evidence, and results. A fixed result cap or one empty page does not establish completeness. Resolve truncation or indexing limits through verifiable alternatives, such as fully paginated listings and body reads. If the tracker genuinely lacks a native relationship type, record that fact and use the remaining applicable sources. Distinguish unsupported features from access failures and API errors.

## Establish query completeness

## 恢复与失败

首次完整发现前，API 失败、分页未完成、权限不足或覆盖无法验证均停止实现，仅继续查询恢复、只读调查与保存证据。未知事项集合不是空集合。

已有完整快照后查询失败：允许该快照中已分配且依赖满足的本地开发/测试继续；暂停新调度、集成、验收写回及交付。保存失败来源、时间和范围，恢复完整查询后核对新增/删除/条款及依赖变化，完成受影响工作的再评估才恢复。

压缩续接且外部状态未变时读取原完整快照、统一状态及必要增量，不重做完整发现。外部状态可能变化的恢复先核对资源与 tracker。初始完整发现后只有能证明全范围覆盖的增量协议才可代替重复查询：保存基准、游标/分页、删除与关系变化的覆盖证明；单页、未验证更新时间过滤均不足。当前工具没有 tracker 增量客户端，缺少覆盖证明时使用完整查询。交付前一律完整核对。

`workflow.py --state <路径> --run-id <运行> discovery --input <事件.json>` 保存门禁：首次 `failed` 无本地可执行事项；完整 `snapshot` 后 `failed` 仅返回原已分配 localTickets；恢复 snapshot 产生 changedTickets，逐项 `reconciled` 后恢复集成。`continuation` 复用快照但验收写回和交付须重新完整核对；外部状态可能变化时先 gate purpose:resume 撤销旧查询资格，恢复 full snapshot 并核对变化后推进。最终 full snapshot 后查询 gate purpose:handoff。snapshot 包含 scope、tickets（事项→条款/关系内容身份）、assigned、mode:full，sources 为 native/bodies/dependencies 三类完整来源及 evidence 路径。工具不建立来源声明的真实性；协调者仍须核对原始完整分页，父事项也纳入集合。

The **discovery snapshot** contains the parent spec's identity, query time and scope, completeness evidence for each source, deduplicated tickets, relationship evidence for each ticket, dependencies, excluded candidates with reasons, and unresolved relationships. Unresolved relationships block affected paths and full-spec handoff; they do not trigger the global stop reserved for query failures.

## Reconcile and recover

On resume, reconcile existing resources through [run resources](resource-management.md), then complete task discovery and reconciliation below. Resource observations govern reuse and cleanup; they do not change query-completeness requirements.

Compare the new snapshot with the run record. Identify added, previously missed, removed, or changed relationships and dependencies. When a ticket disappears, verify whether its parentage changed or a query failed before removing it from the acceptance set, and record the reason. Handle ambiguity and query failures under the rules above.

For each added or previously missed ticket, reconcile current acceptance criteria, matching commits, review coverage, execution evidence, still-applicable user confirmations, and tracker write-back state. Parent acceptance, a closed ticket, or apparently sufficient code cannot replace ticket-level verification. Complete missing implementation and review before final acceptance. Recompute the frontier when tickets or dependencies change.

Preserve commit history and recoverable work. Map each ticket to existing commits rather than redoing delivered code to reconstruct one branch or commit per ticket. Use new commits referencing affected tickets for missing implementation and final fixes. Reuse evidence only when it matches current criteria and unchanged content; final executable acceptance still follows the evidence-validity rules in [acceptance and handoff](acceptance.md).

Keep full-spec handoff pending while reconciliation, relationships, or any ticket's implementation, review, acceptance, or write-back evidence remains unresolved. If the parent is already closed or the PR is ready, record the actual state and correct it under tracker rules and existing authorization. Report blockers when additional permission is needed; distinguish a planned correction from a completed one.
