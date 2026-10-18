# Integration review

At final acceptance, use an independent read-only reviewer in a fresh context by default. Reconcile every reviewable entry in OCR's complete baseline-to-integration inventory under the current rules with matching prior coverage or fresh review. Preserve OCR exclusion reasons and coverage counts. Reuse review only when the diff, requirements, and rules still correspond; file names and an old pass are insufficient.

Freshly review cross-ticket interactions, shared contracts, conflict resolutions, new diffs, and coverage gaps. Separately reviewed modules can still interact incorrectly. Broaden review when uncertain; read the full diff when correspondence cannot be established. Keep independent evidence for each technical criterion.

Return valid findings to the original implementer and retain the reviewer through the same issue's fix loop. Record false-positive reasoning and user decisions. Rerun affected checks. Final fixes may use separate commits referencing the tickets while preserving their initial commits. Enter [fixed-commit acceptance](acceptance.md) when the full inventory is covered, valid findings are resolved, and affected checks pass.
