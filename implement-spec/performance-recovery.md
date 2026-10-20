# Legacy performance recovery

Read when the legacy-record conditions in [performance work](performance.md) fire.

`schemaVersion:1` records remain readable. The first budget event adds phase policy metadata while preserving timestamps, exclusions, measurements, events, and unrelated workflow state. A legacy phase with a recorded default start and no custom limit or user decision becomes autonomous.

Other legacy phases return `decision:reconcile`. Read saved authorization and record `policy` with `mode` and supporting `source`; include `limitMinutes` only for a genuine user budget. A numeric limit or an extension prompted by the old default gate alone does not establish a user-imposed cap. Resolve the policy from existing authorization; ask only if a material ambiguity remains.

Retain legacy values and explicit phase-delivery choices. Reconcile stale waiting summaries with the resulting state. Resume a pause caused solely by the old default gate only when its reason is resolved. Preserve actual user waits and external blocks until their reasons are resolved.
