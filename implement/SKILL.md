---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

开始实现、续接会话以及请求用户验收前，读取并执行 [验收前提与授权续接](../acceptance-preflight.md)，记录前提、入口和已有授权。

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, spawn one read-only subagent with the ticket context to run /open-code-review-delegate. Validate and fix its findings, rerun affected tests.

Use /to-commit to commit your work to the current branch.
