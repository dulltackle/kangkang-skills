# 阶段协作和性能投入

## 性能阶段

进入性能阶段时创建一个共享 phaseId，在仓库外状态文件中持久保存；分析、实现和实验均计入同一时间窗。默认预算 45 分钟、30 分钟检查点，用户可在开始前覆盖。换 agent、并行执行或压缩不重置；仅显式用户等待和外部阻塞可暂停，记录起止及理由。

使用 `scripts/workflow.py --state <绝对路径> --run-id <运行> budget --input <事件.json>`。所有事件包含 `phaseId`、`event`、实际时钟 `at`（含时区）。`start` 可设 `limitMinutes`、`checkpointMinutes`；`pause` 的 reason 是 `user-wait`/`external-block`，`resume` 结束暂停。`status` 输出已用时、checkpoint/tradeoff 及新增实验许可，任何接手者先查询原状态。

`measure` 包含正数 `durationSeconds`、`completeEntry`、`comparisonKey`、原始测量 `source`。比较身份固定入口、源码范围、模型、环境、冷热及并发条件；只有连续三次同身份完整测量才能得出连续两轮改善。中途样本不可比则打断连续性，时间上限仍有效。

检查点报告实际收益与差距。预算到期或两轮改善都不足 5%（含退步）时，停止新增实验，报告来源、收益、剩余要求和继续投入理由，由用户明确继续或分期。`decide` 保存用户原话 source 和 choice；继续须明确 `extensionMinutes`。必要修复、审查和独立工作始终可继续。计划或低收益节点不能改变性能验收；用户未答时保持待决。

## 交接

主要阶段默认更换实现/审查上下文，沿依赖推进独立工作，不为节省 token 全局串行。同问题修复循环保持 reviewer；问题未解决时延后阶段交接。原拥有者完成、取消并确认活动检查，避免重复启动和错误清理。

交接包含目标/阶段/固定提交、接口约定、未解决问题及证据索引；详细日志与探索历史只保留路径，接手者独立判断复用。用 `workflow.py ... handoff --input <包.json>` 保存：`stage`、`target`、`commit`、`contracts`、`unresolved`、`evidence`、`activeChecks`、`implementer`、`reviewer`。证据必须存在并保存哈希；活动检查阻止交接。最终 `stage:acceptance` 必须记录 `crossTicketReview:true`。工具核对声明结构，不能证明 agent 的实际独立性。

协调者唯一维护统一状态，消息围绕完成、阻塞、接口变化；实现者报告状态变化，避免重复广播。最后交给独立上下文审查跨事项共享约定及覆盖缺口，参见 [集成审查](integration-review.md)。
