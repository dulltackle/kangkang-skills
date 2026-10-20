# Maintenance and evaluation

The user-designated maintained source has no Git repository. Preserve that state. Its path, expressed as a JSON string, is:

```json
"/home/forclaw/\u6587\u6863/implement-spec/"
```

Before editing, save recoverable originals and hashes. Record maintained-source changes separately from ClapGrid commits.

Run the public CLI tests for resources, shared state, and evidence, then evaluate scheduling decisions in an isolated context using [the scenarios](evals/scenarios.md). Verify actual host-session persistence and terminal state through creation and query interfaces across separate calls. Local Python return codes and simulated terminal results establish only local behavior.

Run the resource, workflow, and evidence CLI regressions:

```sh
python3 <skill-dir>/evals/test_resources.py -v
python3 <skill-dir>/evals/test_workflow.py -v
python3 <skill-dir>/evals/test_evidence.py -v
```

Tests use temporary files and local Git repositories, without connecting to actual run resources, hosts, or trackers. Tool regressions do not replace isolated behavioral evaluation. For stall and conditional-reading scenarios, record time to the first useful report, repeated attempts, unwarranted pauses, and documents actually loaded. Report these separately from tokens, calls, and elapsed time.

For cost evaluation, use three small fixed scenarios: normal delivery, low-gain optimization, and execution interruption. Preserve original and candidate inputs, raw outputs, and usage under the same model, environment, task, and coverage. Report uncached input, cached input, output tokens, model calls, and actual execution time separately; list waits and explicit external blocks separately. Establish the baseline before fixing improvement targets and comparison conditions. Limit conclusions to the measured samples. Roll out only with repeatable benefits and complete coverage; keep unproven parts as a pilot.

After verification, inspect actual installation metadata; the installed copy's repository does not establish the maintained source. The current manager's `skills-manager-cli skills show implement-spec` identifies a local `source_ref`. Before authorized synchronization, back up the installation, confirm the affected files, and check `--help` for a skill-specific update. Keep the operation scoped to this skill rather than a library-wide sync or update. Record the command, manager identity, old and new hashes, and deployment-link state. Verify preservation of existing content and unrelated skills. Report maintained-source, installed-copy, and actual-host states separately; actual-host acceptance requires verified host behavior.
