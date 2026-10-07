# Acceptance and Handoff

Run after integration review and its fixes. The coordinator owns tracker writes and closure; subagents supply evidence.

验收勾选必须有对应的执行结果、独立技术审查证据或明确用户确认，具体类型按下文判断。Every ticket must have a nonempty acceptance region with every criterion earned before the spec can be handed off.

## 1. Reverify the final state

先按 [task-discovery.md](task-discovery.md) 重新发现完整任务集合，与运行记录对账，而非仅重读原清单。查询不完整时执行全局停止规则；新增、遗漏或关系变化按该文件的恢复流程处理，补齐受影响的实现和审查后重新进入验收。逐票维护当前标准对应的提交、审查、验收证据及写回状态；父 SPEC 的验收、代码覆盖推测或已关闭状态不能替代子票证据。

Re-read each ticket from the tracker. Match evidence to the **exact text** of its current acceptance criteria. Verify added or changed criteria; evidence with no matching criterion pauses that ticket's write-back. Leave unverified criteria unchecked.

最终集成审查与修复完成后，确定集成提交，在该提交的独立检出中重新运行每项可执行验收（包括已勾选项）、全套测试、类型检查和项目要求的其他检查。优先使用项目已有的正式验收入口；否则准备独立检出并按锁定依赖运行项目检查。记录提交、源码身份、命令、环境、结果和日志位置；结果只证明受验提交，不证明后来变化的分支。开发工作区中的指纹对比不能替代独立检出。Earlier worktree results do not replace this verification.

Classify each criterion:

- **`ran`**：可执行要求已实际运行并观察到通过；记录受验提交、命令、结果及环境缺口。未执行、失败或跳过的要求保持未验收，审查结论与用户确认均不能替代执行。
- **`reviewed`**：标准明确、能够通过源码或文档阅读判断的技术要求，由未参与该内容实现的独立审查者验收。证据包含标准原文、受验提交、文件位置、判断依据、审查者与未解决问题；协调者核对对应关系后才能勾选。泛称“OCR 通过”或实施者自述不是逐项验收证据。可以机械判定的要求优先建立确定性检查，并按 `ran` 提供结果。
- **`user`**：产品取舍、主观体验、新增范围、含糊或冲突的标准，以及条款明确要求用户确认的内容，由用户决定或验收。不能通过改分类取消条款中的明确用户确认要求。涉及可执行要求的部分仍须实际运行。
- **失败、未验证或证据不完整**：保持未勾选。旧记录中的 `read` 不自动升级为 `reviewed`；核对当前条款与内容，补充独立审查证据或有效用户确认后再验收。

仅将 `user` 项按任务分组一次询问，保留拒绝或未答复项目未勾选。既有明确确认仅在相关内容未变化时沿用。技术审查发现标准含糊时，先请求澄清，不能自行降低标准；新规则不追溯改变旧任务的验收与关闭状态。

A failing check loses its existing tick: report the regression and its reason. Reopen a previously closed ticket that has lost acceptance, using the tracker's rules. It can close again only after acceptance is earned again.

后续修复使受影响证据失效：对新集成提交重跑受影响标准及项目最终检查，技术阅读项由独立审查者复核相关变化。将结果与当前交付提交对账后才能继续写回和交付。

## 2. Write earned acceptance back

Re-read immediately before each write. Change only exact-matched checkboxes inside the acceptance region; preserve other lists and prose. Use conditional writes when supported. On concurrent edits, reconcile against the fresh body rather than overwriting it with a stale copy.

Append a concise record of commits and branch, executed checks, user confirmations, revoked ticks, and outstanding items. Keep full command evidence in session output and the run record. Follow the repository's language conventions for comments and commit messages.

Verified items may be written while human confirmation is pending; handoff still requires every criterion to be earned.

### External tracker

Commit code and fixes before write-back. If either the body update or comment fails, pause further writes and handoff. Report completed and pending operations; retain landed commits and successful remote writes. On resume, inspect the current state and complete only missing operations.

### Local Markdown tracker

Put acceptance edits and required logs in a separate Conventional Commit, preserving the initial code commits.

Save the affected acceptance and log fragments before editing. If the commit fails, revert only this run's uncommitted write-back. First compare each current fragment with the version this run wrote: reverse it only if they still match. If somebody changed it, preserve the current content and report the conflict.

Preserve the user's staging set. Unrelated staged changes block this close-out commit until resolved; neither include nor unstage them. A formatting-only hook allows one restage-and-retry of this run's files. A refusal leaves the code commits intact and is reported.

## 3. Push and hand off

Start when every ticket is all green, write-back succeeded, and the final work is committed.

交付操作前，按 task-discovery.md 再次确认任务集合及关系未变化，并读取当前验收标准和写回状态。发现变化时返回对账和受影响的验收步骤；只有最新完整集合中的每张票和父 SPEC 均满足各自验收、审查及写回条件，才可将 PR 转 ready、直接关闭任务或宣称完整交付。记录实际关闭状态；等待 PR 合并关闭的票不视为已关闭。

**With a PR:** push the integration branch, then mark the draft ready for review. Report it as awaiting merge. Let the PR workflow close the spec and tickets. A local tracker with a separate closure field records acceptance now and follows its configured PR workflow for closure.

**Without a PR:** push successfully before closing tickets and the spec through the tracker. Set upstream on the first push as configured. With no remote, state that pushing was skipped and proceed with local closure. A refused push pauses handoff, retaining the branch and open tickets; do not force-push or rewrite history.

**Local closure changes files:** after the acceptance commit is landed and pushed where a remote exists, commit the closure edits separately and push them. If that commit or push fails, report the exact local/remote split, keep recovery materials, and leave handoff incomplete.

A partial failure is not a wholesale rollback. Preserve landed commits and successful remote writes; reverse only this run's uncommitted local ticket edits under the concurrency check above. Before retrying, inspect current state to avoid duplicate comments, duplicate closure, or overwritten edits.
