"""Test registration, reconciliation, and cleanup records using temporary resources."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/resources.py"


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / "resources.json"
        self.proof = self.root / "creation.json"
        self.proof.write_text('{"created": true}')

    def call(self, command, payload=None, suffix="", proof=None, run_id="test-run"):
        args = [sys.executable, str(SCRIPT), "--registry", str(self.registry),
                "--run-id", run_id, command]
        if payload is not None:
            source = self.root / (command + suffix + ".json")
            source.write_text(json.dumps(payload))
            args.extend(["--input", str(source)])
            if command != "capture":
                args.extend(["--evidence", str(proof or self.proof)])
        return subprocess.run(args, capture_output=True, text=True)

    def spec(self, rid="A"):
        return {"id": rid, "kind": "worktree", "owner": "author / ticket",
            "purpose": "Test registration", "manager": "managed-host",
            "identity": "host/worktree/" + rid, "location": str(self.root / rid)}

    def report(self, rid="A", **changes):
        value = {"resourceId": rid, "identity": "host/worktree/" + rid,
            "type": "observation", "observedAt": "2026-10-13T00:00:00Z",
            "hostScope": "unverified", "presence": "unknown", "activeUse": "unknown",
            "reason": "Host visibility is unverified"}
        value.update(changes)
        return value

    def data(self):
        return json.loads(self.registry.read_text())

    def test_capture_actual_session_and_recover_registration(self):
        call = {"id":"start", "owner":"author / ticket", "purpose":"check", "location":str(self.root),
            "manager":"exec_command", "operation":"start", "observedAt":"2026-10-18T00:00:00Z",
            "result":{"session_id":123,"output":"running","wall_time_seconds":1}}
        self.assertEqual(self.call("capture", call).returncode,0)
        data=self.data(); self.assertEqual(data["resources"]["start"]["registration"]["handle"],"123")
        self.assertEqual(data["executions"]["start"]["state"],"running")
        self.assertEqual(self.call("capture", call).returncode,0)
        call.update(id="poll",manager="write_stdin",operation="observe",resourceId="start",handle="123",
                    result={"exit_code":0,"output":"done"})
        self.assertEqual(self.call("capture",call).returncode,0)
        self.assertEqual(self.data()["resources"]["start"]["events"][-1]["report"]["presence"],"absent")
        # A local child exit creates only an execution record; outer-host and descendant termination remain unverified.
        call.update(id="local",manager="python-subprocess",operation="start",result={"returncode":0})
        self.assertEqual(self.call("capture",call).returncode,0)
        self.assertEqual(self.data()["executions"]["local"]["state"],"unknown")
        self.assertNotIn("local",self.data()["resources"])

    def test_local_probe_cannot_close_original_host_session(self):
        call = {"id":"session", "owner":"author", "purpose":"check", "location":str(self.root),
            "manager":"exec_command", "operation":"start", "observedAt":"2026-10-18T00:00:00Z",
            "result":{"session_id":123,"output":"running"}}
        self.assertEqual(self.call("capture",call).returncode,0)
        call.update(id="local-probe",operation="observe",resourceId="session",handle="123",result={"exit_code":0})
        self.assertNotEqual(self.call("capture",call).returncode,0)
        self.assertEqual(self.data()["resources"]["session"]["events"],[])

    def test_capture_recovers_failed_run_registration_using_saved_result(self):
        self.registry.write_text(json.dumps(dict(schemaVersion=1,runId='test-run',resources={})))
        call={"id":"created", "owner":"author", "purpose":"check", "location":str(self.root),
            "manager":"exec_command", "operation":"start", "observedAt":"2026-10-18T00:00:00Z",
            "result":{"session_id":456,"output":"running"}}
        self.assertNotEqual(self.call('capture',call,run_id='wrong-run').returncode,0)
        original=(self.root/'capture.json').read_bytes()
        self.assertEqual(self.call('capture',call).returncode,0)
        self.assertEqual((self.root/'capture.json').read_bytes(),original)
        self.assertEqual(len(self.data()['resources']),1)

    def test_capture_real_git_worktree_from_original_command_result(self):
        repo=self.root/'repo';tree=self.root/'worktree'
        subprocess.run(['git','init','-q',str(repo)],check=True)
        subprocess.run(['git','-C',str(repo),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','--allow-empty','-qm','fixture'],check=True)
        created=subprocess.run(['git','-C',str(repo),'worktree','add','--quiet','--detach',str(tree),'HEAD'],capture_output=True,text=True)
        self.assertEqual(created.returncode,0)
        call={"id":"tree", "owner":"author", "purpose":"git fixture", "location":str(tree),"repository":str(repo),
            "manager":"git", "operation":"create", "observedAt":"2026-10-18T00:00:00Z",
            "result":{"exit_code":created.returncode,"output":created.stdout,"stderr":created.stderr}}
        self.assertEqual(self.call('capture',call).returncode,0)
        self.assertEqual(self.data()['resources']['tree']['registration']['location'],str(tree))
        self.assertTrue(json.loads(self.call('inspect').stdout)['resources'][0]['gitRegistered'])

    def test_registration_retry_preserves_original(self):
        self.assertEqual(self.call("register", self.spec()).returncode, 0)
        before = self.registry.read_bytes()
        result = self.call("register", self.spec())
        self.assertEqual(json.loads(result.stdout)["status"], "already-registered")
        self.assertEqual(before, self.registry.read_bytes())

    def test_run_or_identity_conflict_preserves_record(self):
        self.call("register", self.spec())
        before = self.registry.read_bytes()
        self.assertNotEqual(self.call("register", self.spec(), run_id="another").returncode, 0)
        changed = self.spec(); changed["identity"] = "replacement"
        self.assertNotEqual(self.call("register", changed).returncode, 0)
        duplicate = self.spec("B"); duplicate["identity"] = self.spec()["identity"]
        self.assertNotEqual(self.call("register", duplicate).returncode, 0)
        self.assertEqual(before, self.registry.read_bytes())

    def test_concurrent_registration_loses_no_entry(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda n: self.call("register", self.spec(str(n)),
                                                       suffix=str(n)), range(16)))
        self.assertTrue(all(r.returncode == 0 for r in results))
        self.assertEqual(len(self.data()["resources"]), 16)

    def test_failed_registration_can_resume_without_recreation(self):
        failed = self.call("register", self.spec(), proof=self.root / "missing.json")
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(self.registry.exists())
        self.assertEqual(self.call("register", self.spec()).returncode, 0)

    def test_unverified_scope_cannot_assert_inactive(self):
        self.call("register", self.spec())
        result = self.call("record", self.report(activeUse="inactive"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.data()["resources"]["A"]["events"], [])

    def test_cleanup_request_is_not_completed_cleanup(self):
        self.call("register", self.spec())
        result = self.call("record", self.report(type="cleanup", status="removed"))
        self.assertNotEqual(result.returncode, 0)
        report = self.report(type="cleanup", status="removed", hostScope="actual-host",
                             presence="absent", activeUse="inactive")
        self.assertEqual(self.call("record", report).returncode, 0)
        count = len(self.data()["resources"]["A"]["events"])
        self.assertEqual(json.loads(self.call("record", report).stdout)["status"], "already-recorded")
        self.assertEqual(len(self.data()["resources"]["A"]["events"]), count)

    def test_identity_and_observation_time_checked(self):
        self.call("register", self.spec())
        self.assertNotEqual(self.call("record", self.report(identity="different")).returncode, 0)
        self.assertNotEqual(self.call("record", self.report(observedAt="2026-10-13")).returncode, 0)
        self.assertEqual(self.call("record", self.report()).returncode, 0)
        self.assertNotEqual(self.call("record", self.report(observedAt="2026-10-12T00:00:00Z")).returncode, 0)

    def test_retained_resource_does_not_block_later_resource(self):
        for rid in ("A", "B"):
            self.call("register", self.spec(rid))
        self.assertEqual(self.call("record", self.report(type="cleanup", status="retained")).returncode, 0)
        self.assertEqual(self.call("record", self.report("B", type="cleanup", status="removed",
            hostScope="actual-host", presence="absent", activeUse="inactive")).returncode, 0)
        self.assertEqual(len(self.data()["resources"]["B"]["events"]), 1)

    def test_inspect_reports_changed_and_missing_evidence_without_rewriting(self):
        self.call("register", self.spec())
        before = self.registry.read_bytes()
        self.proof.write_text("changed")
        for missing in (False, True):
            if missing:
                self.proof.unlink()
            result = self.call("inspect")
            self.assertEqual(result.returncode, 0)
            row = json.loads(result.stdout)["resources"][0]
            self.assertEqual(row["changedOrMissingEvidence"], [str(self.proof)])
            self.assertEqual(row["activeUse"], "unknown")
            self.assertEqual(before, self.registry.read_bytes())

    def test_empty_registry_is_not_zero_resources_proof(self):
        self.assertNotEqual(self.call("inspect").returncode, 0)

    def test_process_requires_handle_and_correct_cleanup_kind(self):
        spec = self.spec(); spec.update(kind="process", identity="host/session-A/start-time")
        self.assertNotEqual(self.call("register", spec).returncode, 0)
        spec["handle"] = "host-session-A"
        self.assertEqual(self.call("register", spec).returncode, 0)
        report = self.report(identity=spec["identity"], type="cleanup", status="removed",
            hostScope="actual-host", presence="absent", activeUse="inactive")
        self.assertNotEqual(self.call("record", report).returncode, 0)
        report["status"] = "stopped"
        self.assertEqual(self.call("record", report).returncode, 0)

    def test_git_inspection_uses_exact_worktree_path_and_sees_unsaved_content(self):
        repo = self.root / "repository"
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c",
            "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "Test baseline"], check=True)
        # Keep a non-ASCII path fixture while source comments remain English.
        location = self.root / "\u4e2d\u6587\u5de5\u4f5c\u6811"
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "--detach", str(location)],
                       check=True, capture_output=True)
        spec = self.spec();spec.update(manager="git", repository=str(repo), location=str(location))
        self.assertEqual(self.call("register", spec).returncode, 0)
        (location / "\u672a\u4fdd\u5b58.txt").write_text("unsaved")
        row = json.loads(self.call("inspect").stdout)["resources"][0]
        self.assertTrue(row["gitRegistered"])
        self.assertGreater(row["gitStatusBytes"], 0)
        self.assertEqual(row["activeUse"], "unknown")


if __name__ == "__main__":
    unittest.main()
