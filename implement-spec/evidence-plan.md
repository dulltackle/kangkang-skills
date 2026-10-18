# 验收证据计划

在独立 reviewer 给出语义结论后，用 `python3 <skill-dir>/scripts/acceptance_evidence.py --input <清单.json> --output <计划.json>` 核对材料。默认只打印摘要及计划路径；完整材料从原路径按需读取。工具不连接 tracker、不执行写回、不替代项目正式报告校验器。

输入为 `ticket`（完整身份）、`commit`（候选提交）、`criteria`（每条 id、准确 text、proofs ID 列表）、`proofs`、`review`。条款/证据 ID 唯一。证据包含 id/path/sha256、commitPointer/statusPointer（原 JSON 报告的 JSON Pointer）及 sources（原始文件 path/sha256）。原报告必须实际 passed，提交匹配；原报告内部完整性仍须通过项目现有校验器。文本/二进制来源只检查哈希，不强制解析 JSON。

review 指向保存的独立报告 path/sha256；报告包含 reviewer、implementer、commit、criteria。每条结论含准确 text、decision:earned、reason 和 locations。工具仅核对声明关系，协调者须验证 reviewer 的实际独立身份及判断依据，不能自己构造一份 review 代替审查。

旧证据须显式携带 reuse：originalCommit、targetCommit、source。该来源 JSON 保留 originalCommit/targetCommit/unchanged:true/scope（条款 ID）及实际内容比对依据；要求仍对应当前范围。项目正式验收若要求同一提交，本工具的通用内容复用不能放宽该规则。保留原报告来源、执行身份和完成时间，不重写为本次新运行。

输出列出来源、缺口、条款原文和 proposedCheckboxes，始终 written:false。材料完整仍须独立语义判断。写回前按 [验收协议](acceptance.md) 重新读取当前条款、精确匹配、遵守授权并核对实际写回结果。
