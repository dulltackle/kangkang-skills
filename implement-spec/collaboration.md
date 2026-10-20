# 阶段交接

功能实现转向性能工作或最终验收时，默认使用新的实现和审查上下文；同一问题的修复循环保留原 reviewer，解决后再交接。沿依赖图推进独立工作。原 owner 先完成或取消活动检查，并确认实际状态。

传递紧凑 Handoff packet：目标、阶段、固定 commit、interface 约定、未解决问题和证据索引。详细日志与探索历史保留在路径后，接收者独立判断证据能否复用；未解决的[停滞记录](progress.md)随问题延续。

通过 `workflow.py ... handoff --input <packet.json>` 保存 `stage`、`target`、`commit`、`contracts`、`unresolved`、`evidence`、`activeChecks`、`implementer` 和 `reviewer`。证据须存在并记录 hash，活动检查阻止交接。最终 `stage:acceptance` 需要 `crossTicketReview:true`。工具检查声明和结构，agent 实际独立性需要另有证据。

协调者独自维护共享 run record；实现者在完成、阻塞或 interface 变化时报告一次状态变化。最终使用独立上下文按[集成审查](integration-review.md)检查跨票约定与覆盖缺口。
