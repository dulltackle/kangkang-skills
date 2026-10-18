#!/usr/bin/env python3
"""Register run resources and evidence without creating, stopping, or removing host resources."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
import re
from types import SimpleNamespace
from pathlib import Path
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def evidence(path):
    path = Path(path).resolve(strict=True)
    require(path.is_file(), "Evidence must be a saved file")
    return {"path": str(path), "sha256": digest(path)}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def absolute(value):
    require(nonempty(value) and Path(value).is_absolute(), "Location must be an absolute path")
    return os.path.normpath(value)


@contextmanager
def locked(path):
    # A POSIX advisory lock releases on exit and prevents concurrent registry overwrites.
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield


def save(path, data):
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load(path, run_id):
    data = read_json(path) if path.exists() else {
        "schemaVersion": 1, "runId": run_id, "resources": {}}
    require(data.get("schemaVersion") == 1 and data.get("runId") == run_id,
            "Registry version or run identity does not match")
    require(isinstance(data.get("resources"), dict), "Invalid resource collection")
    return data


def register(data, args):
    spec = read_json(args.input)
    require(isinstance(spec, dict), "Registration input must be an object")
    allowed = {"id", "kind", "owner", "purpose", "manager", "identity",
               "location", "repository", "handle"}
    require(set(spec) <= allowed, "Registration input contains unknown fields")
    for key in ("id", "owner", "purpose", "manager", "identity"):
        require(nonempty(spec.get(key)), "Missing registration field: " + key)
    require(spec.get("kind") in ("worktree", "process"), "Unsupported resource kind")
    spec["location"] = absolute(spec.get("location"))
    if spec["kind"] == "process":
        require(nonempty(spec.get("handle")), "Processes require a host session or job handle")
    if spec["manager"] == "git":
        require(spec["kind"] == "worktree", "The git manager applies only to worktrees")
        spec["repository"] = absolute(spec.get("repository"))
    proof = evidence(args.evidence)
    resources = data["resources"]
    old = resources.get(spec["id"])
    if old:
        require(old["registration"] == spec and old["creationEvidence"] == proof,
                "Resource identity is already registered; preserve the record and use a new ID for a new resource")
        return {"id": spec["id"], "status": "already-registered"}
    require(not any(r["registration"]["identity"] == spec["identity"]
                    for r in resources.values()), "This resource identity is already registered under another ID")
    resources[spec["id"]] = {"registration": spec, "creationEvidence": proof,
        "registeredAt": datetime.now(timezone.utc).isoformat(), "events": []}
    return {"id": spec["id"], "status": "registered"}


def record(data, args):
    report = read_json(args.input)
    require(isinstance(report, dict), "Observation or cleanup input must be an object")
    entry = data["resources"].get(report.get("resourceId"))
    require(entry is not None, "Resource is not registered")
    require(report.get("identity") == entry["registration"]["identity"],
            "Observation does not match the registered resource identity")
    require(nonempty(report.get("observedAt")), "Missing actual observation time")
    stamp = datetime.fromisoformat(report["observedAt"].replace("Z", "+00:00"))
    require(stamp.tzinfo is not None, "Observation time must include a timezone")
    if entry["events"]:
        previous = entry["events"][-1]["report"]["observedAt"]
        require(stamp >= datetime.fromisoformat(previous.replace("Z", "+00:00")),
                "An older observation cannot replace a newer resource state")
    require(report.get("type") in ("observation", "cleanup"), "Invalid event type")
    require(report.get("hostScope") in ("actual-host", "unverified"), "Host visibility must be specified")
    require(report.get("presence") in ("present", "absent", "unknown"), "Invalid presence state")
    require(report.get("activeUse") in ("active", "inactive", "unknown"), "Invalid active-use state")
    require(nonempty(report.get("reason")), "Missing observation or disposition reason")
    if report["hostScope"] == "unverified":
        require(report["activeUse"] == "unknown", "Unverified host visibility cannot establish active-use state")
    if report["type"] == "cleanup":
        status = report.get("status")
        require(status in ("removed", "stopped", "retained", "failed"), "Invalid cleanup status")
        if status in ("removed", "stopped"):
            require(report["hostScope"] == "actual-host" and report["presence"] == "absent"
                    and report["activeUse"] == "inactive", "Completed cleanup requires an actual-host postcondition observation")
            expected = "removed" if entry["registration"]["kind"] == "worktree" else "stopped"
            require(status == expected, "Cleanup status does not match the resource kind")
    proof = evidence(args.evidence)
    recovery = [evidence(p) for p in args.recovery]
    event = {"report": report, "evidence": proof, "recovery": recovery,
             "recordedAt": datetime.now(timezone.utc).isoformat()}
    if entry["events"] and all(entry["events"][-1].get(k) == event[k]
                               for k in ("report", "evidence", "recovery")):
        return {"id": report["resourceId"], "status": "already-recorded"}
    entry["events"].append(event)
    return {"id": report["resourceId"], "status": "recorded"}


def inspect(data):
    rows = []
    for rid, entry in data["resources"].items():
        spec = entry["registration"]
        events = entry["events"]
        row = {"id": rid, "kind": spec["kind"], "location": spec["location"],
               "latest": events[-1]["report"] if events else None,
               "localPathExists": Path(spec["location"]).exists(),
               "activeUse": "unknown", "hostScope": "unverified"}
        proofs = [entry["creationEvidence"]]
        for event in events:
            proofs.extend([event["evidence"], *event["recovery"]])
        bad = set()
        for proof in proofs:
            try:
                if digest(proof["path"]) != proof["sha256"]:
                    bad.add(proof["path"])
            except OSError:
                bad.add(proof["path"])
        row["changedOrMissingEvidence"] = sorted(bad)
        # Local paths and Git output cannot establish the absence of active host processes.
        if spec["manager"] == "git":
            try:
                raw = subprocess.check_output(["git", "-C", spec["repository"],
                    "worktree", "list", "--porcelain", "-z"], stderr=subprocess.PIPE)
                row["gitRegistered"] = ("worktree " + spec["location"]).encode() in raw.split(b"\0")
                if row["gitRegistered"]:
                    status = subprocess.check_output(["git", "-C", spec["location"],
                        "status", "--porcelain=v1", "--ignored", "-z"], stderr=subprocess.PIPE)
                    row["gitStatusBytes"] = len(status)
                    row["head"] = subprocess.check_output(["git", "-C", spec["location"],
                        "rev-parse", "HEAD"], stderr=subprocess.PIPE, text=True).strip()
            except (OSError, subprocess.CalledProcessError) as error:
                row["gitCheckError"] = str(error)
        rows.append(row)
    return {"runId": data["runId"], "count": len(rows), "resources": rows,
            "executionCount": len(data.get("executions", {})),
            "note": "Read-only local checks; historical events neither establish current host state nor authorize cleanup"}


def capture(data, args):
    """Capture an original interface result; persist it first and retry the same input after registration failure."""
    call = read_json(args.input)
    for field in ('id','owner','purpose','manager','operation','observedAt','location'):
        require(nonempty(call.get(field)), 'Missing capture field: '+field)
    require(re.fullmatch(r'[A-Za-z0-9_-]{1,128}',call['id']), 'Invalid capture ID')
    require(isinstance(call.get('result'),dict), 'Capture requires the actual result object')
    when = datetime.fromisoformat(call['observedAt'].replace('Z','+00:00'))
    require(when.tzinfo is not None, 'Capture time must include timezone')
    directory = args.registry.resolve().with_suffix('.results')
    directory.mkdir(mode=0o700,parents=True,exist_ok=True)
    raw = directory/(call['id']+'.json')
    content = (json.dumps(call,ensure_ascii=False,indent=2)+'\n').encode()
    if raw.exists():
        require(raw.read_bytes()==content, 'Capture ID conflicts with saved original; preserve it')
    else:
        fd=os.open(raw,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(content);stream.flush();os.fsync(stream.fileno())
    proof=evidence(raw)
    runs=data.setdefault('executions',{})
    if call['id'] in runs:
        require(runs[call['id']]['source']==proof,'Capture original changed')
        return dict(id=call['id'],status='already-captured',source=proof)
    result=call['result']; manager=call['manager']; operation=call['operation']
    host = manager in ('exec_command','write_stdin')
    handle=result.get('session_id')
    ended=host and isinstance(result.get('exit_code'),int) and not isinstance(result.get('exit_code'),bool)
    state='ended' if ended else 'running' if host and handle is not None else 'unknown'
    if operation=='observe':
        rid=call['resourceId']; entry=data['resources'].get(rid)
        require(entry is not None,'Unknown resource; recover its creation registration first')
        spec=entry['registration']
        require(spec['kind']=='process' and spec['manager']=='exec_command' and manager=='write_stdin','Original session interface required')
        require(str(call.get('handle'))==spec['handle'],'Observation handle mismatch')
        require(handle is None or str(handle)==spec['handle'],'Returned session changed')
        report=dict(resourceId=rid,identity=spec['identity'],type='observation',observedAt=call['observedAt'],
            hostScope='actual-host' if ended or handle is not None else 'unverified',
            presence='absent' if ended else 'present' if handle is not None else 'unknown',
            activeUse='inactive' if ended else 'active' if handle is not None else 'unknown',
            reason='Original host session result; session termination does not prove all descendants stopped')
        event_file=directory/(call['id']+'.observation.json')
        save(event_file,report)
        record(data,SimpleNamespace(input=event_file,evidence=raw,recovery=[]))
    elif host and handle is not None:
        require(manager=='exec_command' and operation=='start','Register from original exec_command creation')
        spec=dict(id=call['id'],kind='process',owner=call['owner'],purpose=call['purpose'],manager=manager,
            identity=data['runId']+'/exec_command/'+str(handle)+'/'+call['observedAt'],
            handle=str(handle),location=absolute(call['location']))
        spec_file=directory/(call['id']+'.registration.json');save(spec_file,spec)
        register(data,SimpleNamespace(input=spec_file,evidence=raw))
    elif manager=='git' and operation=='create':
        require(result.get('exit_code')==0,'Git creation command must have completed successfully')
        location=absolute(call['location']); repository=absolute(call['repository'])
        listing=subprocess.check_output(['git','-C',repository,'worktree','list','--porcelain','-z'])
        require(('worktree '+location).encode() in listing.split(b'\0'),'Worktree not registered in Git')
        head=subprocess.check_output(['git','-C',location,'rev-parse','HEAD'],text=True).strip()
        spec=dict(id=call['id'],kind='worktree',owner=call['owner'],purpose=call['purpose'],manager='git',
            identity=data['runId']+'/git/'+location+'/'+head+'/'+call['observedAt'],location=location,repository=repository)
        spec_file=directory/(call['id']+'.registration.json');save(spec_file,spec)
        register(data,SimpleNamespace(input=spec_file,evidence=raw));state='managed'
    runs[call['id']]=dict(source=proof,state=state,manager=manager,operation=operation,
        resourceId=call.get('resourceId',call['id'] if call['id'] in data['resources'] else None))
    return dict(id=call['id'],status='captured',state=state,source=proof,
        resourceId=runs[call['id']]['resourceId'],descendants='unknown')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("register", "record"):
        command = subs.add_parser(name)
        command.add_argument("--input", required=True, type=Path)
        command.add_argument("--evidence", required=True, type=Path)
        if name == "record":
            command.add_argument("--recovery", action="append", default=[], type=Path)
    capture_parser = subs.add_parser("capture")
    capture_parser.add_argument("--input", required=True, type=Path)
    subs.add_parser("inspect")
    args = parser.parse_args()
    try:
        path = args.registry.resolve()
        require(nonempty(args.run_id), "Run identity must be nonempty")
        if args.command == "inspect":
            require(path.is_file(), "Registry is missing; this does not establish that the run has no resources")
            result = inspect(load(path, args.run_id))
        else:
            with locked(path):
                data = load(path, args.run_id)
                result = {"register": register, "record": record, "capture": capture}[args.command](data, args)
                save(path, data)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print("Resource registry error: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
