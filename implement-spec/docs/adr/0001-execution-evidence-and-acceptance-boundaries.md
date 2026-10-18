---
status: accepted
---

# Separate execution facts, managed resources, and acceptance judgments

Automation records execution facts, tracks managed resources, and checks evidence correspondence. Independent reviewers judge semantic requirements; ticket write-back follows established authorization. Short synchronous commands need execution records rather than persistent-resource cleanup. Preserve unknown host terminal states. This separation reduces model bookkeeping while keeping logs, child-process return codes, and material completeness distinct from outer-host termination and earned acceptance.

The user confirmed this decision and the overall design in [ClapGrid #158](https://github.com/dulltackle/ClapGrid/issues/158). Implementation entered verification and delivery. Collect functional and cost-benefit evidence separately; unproven benefits remain a pilot. T1 initially covers current Codex/Linux and existing project entry points. T2 produces correspondence reports and acceptance write-back plans.
