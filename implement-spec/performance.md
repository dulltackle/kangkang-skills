# 性能工作

持续推进已授权的性能工作，直至约定验收标准满足。周期复盘和低收益信号用于调整方法，不要求用户续期授权；满足标准后进入验收和交付。停滞时遵循入口的[汇报规则](progress.md)。

创建共享 `phaseId` 并保存在仓库外。分析、实现和实验累计同一阶段的活动时间；换 agent、并行工作或上下文压缩沿用记录。只排除显式用户等待和外部阻塞，记录起止时间与原因。

使用 `scripts/workflow.py --state <absolute-path> --run-id <run-id> budget --input <event.json>`。事件包含 `phaseId`、`event` 和带时区的实际时间 `at`。接手 agent 先查 `status`。`start` 默认 `mode:autonomous`，无时间上限，`checkpointMinutes:30` 是复盘间隔。`pause` 的原因限于 `user-wait` 或 `external-block`；`resume` 结束暂停。`status` 返回累计时间、复盘原因、待决状态及是否允许新实验。

**旧记录恢复：** 遇到缺少当前阶段策略元数据的旧记录，或 `status` 返回 `decision:reconcile` 时，读取[旧性能记录迁移](performance-recovery.md)。新阶段及已有当前策略的记录无需加载它。

## 进展复盘

评估测量可靠性、收益、剩余验收差距和下一实验的依据。报告实质发现并继续工作，以 `review` 保存简洁 `summary`、具体 `nextAction` 和原始证据 `source`。这会确认当前复盘信号，并从当前累计活动时间安排下一检查点，保留总时长与测量历史。

`measure` 包含正数 `durationSeconds`、`completeEntry`、`comparisonKey` 和原始测量 `source`。保持完整入口、源码范围、模型、环境、缓存状态及并发条件一致。同一比较身份下连续三个完整测量建立两轮收益；不完整或不可比样本打断序列。

两轮收益低于 5%（包括回退）提前触发复盘。结合噪声与验收差距定位瓶颈、修正假设或改变方法，每次重复实验须有具体验证目的。`review` 消耗当前低收益信号，下一信号需要三个新的可比样本；这不代表未解决的停滞已消失，继续保留对应 blocker。复盘不改变实验授权或验收标准。

## 用户预算

仅用户明确设置的时间预算构成硬上限。以 `mode:bounded`、正数 `limitMinutes` 和包含用户原话的 `source` 启动；协调者核实原话确实设定了上限。复盘间隔可以超过较短的预算。到达上限后，停止预算范围内的新实验，报告收益、差距和下一步建议；仅继续预算范围外的工作。若上限覆盖整个任务，修复、审查和独立工作也在其中。

`decide` 保存用户 `choice` 与原始 `source`。有界阶段的 `continue` 需要正数 `extensionMinutes`；`autonomous` 需要用户授权取消时限；`phase` 保留用户选择的阶段性交付。保留测量与决定历史。`review` 和重复 `start` 都不续期预算。策略更新不自动恢复用户选择停止的阶段，授权也不自动解除已有暂停；原因解决后按实际情况记录 `decide` 或 `resume`。
