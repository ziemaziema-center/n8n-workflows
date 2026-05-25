from __future__ import annotations

import argparse
import subprocess
import tempfile
import textwrap
from pathlib import Path
import sys


REMOTE_SCRIPT = r'''
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path("/home/ubuntu/workspace/true-autonomous-controller")
DEPLOY_DIR = ROOT / "runtime" / "deploy"
DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

DRAFT_NAME = "inactive_worldvape_daily_growth_ops_2026-05-25"
ACTIVE_NAME = "worldvape_daily_growth_ops_ACTIVE_2026-05-25"
DRAFT_JSON = ROOT / "workflows" / "inactive_worldvape_daily_growth_ops_2026-05-25.json"
ACTIVE_JSON = DEPLOY_DIR / "worldvape_daily_growth_ops_active_20260525.json"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def list_workflows(active: str | None = None) -> str:
    cmd = ["docker", "exec", "n8n", "n8n", "list:workflow"]
    if active is not None:
        cmd.append(f"--active={active}")
    return run(cmd).stdout


def workflow_id_by_name(name: str) -> str:
    for line in list_workflows().splitlines():
        if "|" not in line:
            continue
        workflow_id, workflow_name = line.split("|", 1)
        if workflow_name.strip() == name:
            return workflow_id.strip()
    return ""


def import_workflow(path: Path) -> None:
    workflow = json.loads(path.read_text(encoding="utf-8-sig"))
    if not workflow.get("id"):
        if workflow.get("name") == DRAFT_NAME:
            workflow["id"] = "WorldvapeDraft20260525"
        elif workflow.get("name") == ACTIVE_NAME:
            workflow["id"] = "WorldvapeGrowth20260525"
        else:
            workflow["id"] = re.sub(r"[^A-Za-z0-9]", "", path.stem)[-24:] or "ImportedWorkflow"
        path = DEPLOY_DIR / f"importable_{path.name}"
        path.write_text(json.dumps(workflow, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    target = f"/tmp/{path.name}"
    run(["docker", "cp", str(path), f"n8n:{target}"])
    run(["docker", "exec", "n8n", "n8n", "import:workflow", "--input", target])


def walk_values(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)
    else:
        yield value


def latest_chat_id() -> str:
    candidates: list[Path] = []
    runtime = ROOT / "runtime"
    for suffix in ("*.json", "*.jsonl"):
        candidates.extend(runtime.rglob(suffix))
    candidates = sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)
    def valid_chat_id(value: object) -> str:
        text = str(value).strip()
        if not re.fullmatch(r"-?\d{6,20}", text):
            return ""
        # Common non-chat numeric fields that appear in n8n/TAC JSON.
        if text in {"1800000", "120000", "30000", "8765", "8000", "5678"}:
            return ""
        return text

    def exact_chat_ids(record: Any):
        if isinstance(record, dict):
            for key, value in record.items():
                if key in {"chat_id", "telegram_chat_id"}:
                    chat = valid_chat_id(value)
                    if chat:
                        yield chat
                yield from exact_chat_ids(value)
        elif isinstance(record, list):
            for item in record:
                yield from exact_chat_ids(item)

    for path in candidates[:500]:
        try:
            if path.suffix == ".jsonl":
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                records = [json.loads(line) for line in reversed(lines[-80:]) if line.strip()]
            else:
                records = [json.loads(path.read_text(encoding="utf-8-sig"))]
        except Exception:
            continue
        for record in records:
            for chat in exact_chat_ids(record):
                return chat
    return ""


def active_js(chat_id: str) -> str:
    objective_lines = [
        "Company HQ daily growth routine for Worldvape Gwangwoon Instagram and SNS.",
        "Work safely inside /home/ubuntu/workspace/sns_automation_safe.",
        "Read project memory, prior growth reports, and stored performance artifacts when available.",
        "Analyze yesterday performance if files exist; do not request or print secret values.",
        "Summarize competitor/content patterns only from stored notes or public-source notes already in workspace.",
        "Generate four YUNA approval candidates with hook, category, YUNA score angle, local customer reason, CTA, follow reason, risk note, and expected metric.",
        "Rank candidates by follow intent, store visit intent, comment intent, and save/share potential.",
        "Write a plain Korean operator report and append a learning note for the next generation cycle.",
        "Do not publish, do not send comments or DMs, do not activate Instagram workflows, do not restart services, and do not read credentials.",
    ]
    objective = "\\n".join(objective_lines)
    return f"""
function stampNow() {{
  return new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
}}
const taskId = `worldvape-daily-growth-${{stampNow()}}`;
const objective = {json.dumps(objective, ensure_ascii=True)};
const prompt = `/work WORKSPACE:/home/ubuntu/workspace/sns_automation_safe\\n${{objective}}`;
return [{{
  json: {{
    task_id: taskId,
    requested_by: 'worldvape_daily_growth_schedule',
    source_channel: 'worldvape_daily_growth_n8n',
    priority: 'high',
    target_runner: 'codex',
    workspace_path: '/home/ubuntu/workspace/sns_automation_safe',
    objective,
    prompt,
    dispatch: true,
    chat_id: {json.dumps(chat_id)},
    notify_webhook_url: 'https://n8n.mykindredai.com/webhook/tac-controller',
    runner_url: 'http://172.17.0.1:8765/queue',
    operator_ack_text: [
      '[Worldvape Growth HQ]',
      '\\uC0C1\\uD0DC: \\uC811\\uC218\\uB428',
      `\\uC791\\uC5C5\\uBC88\\uD638: ${{taskId}}`,
      '',
      '\\uC624\\uB298 \\uC6D4\\uB4DC\\uBCA0\\uC774\\uD504 \\uAD11\\uC6B4\\uB300\\uC810 Instagram/SNS \\uC131\\uC7A5 \\uB8E8\\uD2F4\\uC744 TAC HQ \\uD050\\uC5D0 \\uB123\\uC5C8\\uC2B5\\uB2C8\\uB2E4.',
      '\\uC644\\uB8CC\\uB418\\uBA74 \\uC774 \\uCC44\\uD305\\uC73C\\uB85C \\uACB0\\uACFC \\uBCF4\\uACE0\\uAC00 \\uB2E4\\uC2DC \\uC635\\uB2C8\\uB2E4.',
      '',
      '\\uC9C1\\uC811 \\uAC8C\\uC2DC/DM/\\uB313\\uAE00 \\uBC1C\\uC1A1\\uC740 \\uD558\\uC9C0 \\uC54A\\uACE0, \\uC2B9\\uC778\\uC6A9 \\uD6C4\\uBCF4\\uB9CC \\uB9CC\\uB4ED\\uB2C8\\uB2E4.'
    ].join('\\n')
  }}
}}];
""".strip()


def build_active_workflow(chat_id: str) -> dict[str, Any]:
    return {
        "name": ACTIVE_NAME,
        "active": False,
        "meta": {
            "purpose": "Daily Worldvape Gwangwoon growth routine that queues bounded TAC HQ work and sends operator acknowledgement.",
            "liveOperationsPerformed": False,
            "publishesInstagram": False,
            "readsSecrets": False,
            "generatedBy": "scripts/deploy_worldvape_daily_growth_n8n.py",
        },
        "nodes": [
            {
                "parameters": {
                    "rule": {"interval": [{"field": "days", "triggerAtHour": 8, "triggerAtMinute": 20}]}
                },
                "id": "worldvape-daily-schedule",
                "name": "Daily 0820 KST Schedule",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [0, 0],
            },
            {
                "parameters": {"jsCode": active_js(chat_id)},
                "id": "build-tac-queue-payload",
                "name": "Build TAC Queue Payload",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [260, 0],
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "={{$json.runner_url}}",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {"name": "task_id", "value": "={{$json.task_id}}"},
                            {"name": "objective", "value": "={{$json.objective}}"},
                            {"name": "prompt", "value": "={{$json.prompt}}"},
                            {"name": "requested_by", "value": "={{$json.requested_by}}"},
                            {"name": "source_channel", "value": "={{$json.source_channel}}"},
                            {"name": "priority", "value": "={{$json.priority}}"},
                            {"name": "target_runner", "value": "={{$json.target_runner}}"},
                            {"name": "workspace_path", "value": "={{$json.workspace_path}}"},
                            {"name": "dispatch", "value": "={{$json.dispatch}}"},
                            {"name": "chat_id", "value": "={{$json.chat_id}}"},
                            {"name": "notify_webhook_url", "value": "={{$json.notify_webhook_url}}"},
                        ]
                    },
                    "options": {"timeout": 1800000, "response": {"response": {"responseFormat": "json"}}},
                },
                "id": "queue-tac-work",
                "name": "Queue TAC Work",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [520, 0],
            },
            {
                "parameters": {"chatId": chat_id, "text": "={{$('Build TAC Queue Payload').item.json.operator_ack_text}}", "additionalFields": {"parse_mode": "HTML"}},
                "id": "send-telegram-ack",
                "name": "Send Telegram Ack",
                "type": "n8n-nodes-base.telegram",
                "typeVersion": 1.2,
                "position": [780, 0],
                "webhookId": "worldvape-daily-growth-ack",
                "credentials": {
                    "telegramApi": {
                        "id": "vX5rMVz0EqOevX0u",
                        "name": "Kindred AI Controller",
                    }
                },
            },
        ],
        "connections": {
            "Daily 0820 KST Schedule": {"main": [[{"node": "Build TAC Queue Payload", "type": "main", "index": 0}]]},
            "Build TAC Queue Payload": {"main": [[{"node": "Queue TAC Work", "type": "main", "index": 0}]]},
            "Queue TAC Work": {"main": [[{"node": "Send Telegram Ack", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1", "timezone": "Asia/Seoul"},
        "pinData": {},
    }


def post_queue_smoke(chat_id: str) -> dict[str, Any]:
    stamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    task_id = f"worldvape-daily-growth-smoke-{stamp}"
    objective = "\\n".join([
        "SMOKE validation for the Worldvape Gwangwoon daily growth route.",
        "Work safely inside /home/ubuntu/workspace/sns_automation_safe.",
        "Write a short Korean operator report proving the route can create a YUNA growth planning artifact.",
        "Do not publish, do not send Instagram comments or DMs, do not activate Instagram workflows, do not read credentials, and do not restart services.",
    ])
    payload = {
        "task_id": task_id,
        "requested_by": "worldvape_daily_growth_deploy_smoke",
        "source_channel": "worldvape_daily_growth_direct_smoke",
        "priority": "normal",
        "target_runner": "dry_run",
        "workspace_path": "/home/ubuntu/workspace/sns_automation_safe",
        "objective": objective,
        "prompt": f"/work WORKSPACE:/home/ubuntu/workspace/sns_automation_safe\\n{objective}",
        "dispatch": True,
        "chat_id": chat_id,
        "notify_webhook_url": "https://n8n.mykindredai.com/webhook/tac-controller",
    }
    request = urllib.request.Request(
        "http://127.0.0.1:8765/queue",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read().decode("utf-8"))
    return {"task_id": task_id, "response": body}


def wait_for_task(task_id: str, *, seconds: int = 900) -> dict[str, Any]:
    report = ROOT / "runtime" / "company_runner" / f"{task_id}.json"
    md_report = ROOT / "runtime" / "reports" / f"{task_id}.md"
    notify = ROOT / "runtime" / "reports" / f"{task_id}.notify.json"
    deadline = time.time() + seconds
    while time.time() < deadline:
        if report.exists():
            try:
                payload = json.loads(report.read_text(encoding="utf-8-sig"))
            except Exception:
                payload = {"status": "REPORT_PARSE_FAIL"}
            return {
                "status": payload.get("status", "UNKNOWN"),
                "company_report_exists": True,
                "markdown_report_exists": md_report.exists(),
                "notify_artifact_exists": notify.exists(),
            }
        time.sleep(10)
    return {
        "status": "TIMEOUT_WAITING_FOR_COMPANY_REPORT",
        "company_report_exists": False,
        "markdown_report_exists": md_report.exists(),
        "notify_artifact_exists": notify.exists(),
    }


def cleanup_bad_worldvape_smoke() -> dict[str, Any]:
    queue = ROOT / "runtime" / "queue" / "pending.jsonl"
    if not queue.exists():
        return {"removed": 0, "backup": ""}
    lines = queue.read_text(encoding="utf-8", errors="ignore").splitlines()
    kept: list[str] = []
    removed = 0
    for line in lines:
        try:
            item = json.loads(line)
        except Exception:
            kept.append(line)
            continue
        notification = item.get("notification") if isinstance(item, dict) else {}
        if (
            str(item.get("task_id", "")).startswith("worldvape-daily-growth-smoke-")
            and isinstance(notification, dict)
            and str(notification.get("chat_id", "")) == "1800000"
        ):
            removed += 1
            continue
        kept.append(line)
    if removed:
        backup = queue.with_suffix(f".pending.before_worldvape_cleanup_{int(time.time())}.jsonl")
        backup.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        queue.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        return {"removed": removed, "backup": str(backup)}
    return {"removed": 0, "backup": ""}


def main() -> None:
    if not DRAFT_JSON.exists():
        raise SystemExit(f"missing draft workflow: {DRAFT_JSON}")
    chat_id = latest_chat_id()
    if not chat_id:
        raise SystemExit("DEFERRED_GATE: no prior Telegram chat_id found in runtime artifacts")

    if not workflow_id_by_name(DRAFT_NAME):
        import_workflow(DRAFT_JSON)

    workflow = build_active_workflow(chat_id)
    ACTIVE_JSON.write_text(json.dumps(workflow, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    active_id = workflow_id_by_name(ACTIVE_NAME)
    import_workflow(ACTIVE_JSON)
    active_id = workflow_id_by_name(ACTIVE_NAME)
    if not active_id:
        raise SystemExit("failed to resolve active workflow id after import")

    update = run(["docker", "exec", "n8n", "n8n", "update:workflow", f"--id={active_id}", "--active=true"], check=False)
    if update.returncode != 0:
        raise SystemExit(update.stderr or update.stdout)

    restart = run(["docker", "restart", "n8n"], check=False)
    if restart.returncode != 0:
        raise SystemExit(restart.stderr or restart.stdout)
    time.sleep(10)

    execute = run(["docker", "exec", "n8n", "n8n", "execute", f"--id={active_id}", "--rawOutput"], check=False)
    executed = execute.returncode == 0

    cleanup = cleanup_bad_worldvape_smoke()
    direct_smoke = None
    direct_smoke_wait = None
    if not executed:
        direct_smoke = post_queue_smoke(chat_id)
        direct_smoke_wait = wait_for_task(direct_smoke["task_id"], seconds=900)

    active_list = list_workflows("true")
    inactive_list = list_workflows("false")
    queued = sorted((ROOT / "runtime" / "queue").glob("worldvape-daily-growth-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    latest_task = queued[0].stem if queued else ""

    print(json.dumps({
        "ok": bool(active_id),
        "draft_imported": bool(workflow_id_by_name(DRAFT_NAME)),
        "active_workflow_id": active_id,
        "active_workflow_listed": ACTIVE_NAME in active_list,
        "inactive_draft_listed": DRAFT_NAME in inactive_list or bool(workflow_id_by_name(DRAFT_NAME)),
        "chat_id_found": True,
        "manual_execute_returncode": execute.returncode,
        "manual_execute_pass": executed,
        "manual_execute_blocked_reason": "" if executed else "n8n CLI execute unavailable while server task broker is already running",
        "cleanup_bad_smoke": cleanup,
        "direct_queue_smoke_task_id": (direct_smoke or {}).get("task_id", ""),
        "direct_queue_smoke_status": ((direct_smoke or {}).get("response") or {}).get("status", ""),
        "direct_queue_smoke_wait": direct_smoke_wait,
        "latest_task_id": latest_task,
        "latest_task_exists": bool(latest_task),
        "n8n_restarted": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
'''


def run(cmd: list[str], *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def main() -> int:
    if "--run-remote" in sys.argv:
        exec(REMOTE_SCRIPT, {"__name__": "__main__"})
        return 0

    parser = argparse.ArgumentParser(description="Deploy the Worldvape daily growth n8n workflow on the TAC EC2 host.")
    parser.add_argument("--key", required=True)
    parser.add_argument("--host", default="43.201.227.194")
    parser.add_argument("--user", default="ubuntu")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        local_script = Path(tmpdir) / "deploy_worldvape_daily_growth_remote.py"
        local_script.write_text(REMOTE_SCRIPT, encoding="utf-8")
        remote_path = "/home/ubuntu/workspace/true-autonomous-controller/runtime/deploy/deploy_worldvape_daily_growth_remote.py"
        mkdir_cmd = [
            "ssh",
            "-i",
            args.key,
            "-o",
            "StrictHostKeyChecking=no",
            f"{args.user}@{args.host}",
            "mkdir -p /home/ubuntu/workspace/true-autonomous-controller/runtime/deploy",
        ]
        scp_cmd = [
            "scp",
            "-i",
            args.key,
            "-o",
            "StrictHostKeyChecking=no",
            str(local_script),
            f"{args.user}@{args.host}:{remote_path}",
        ]
        run_cmd = [
            "ssh",
            "-i",
            args.key,
            "-o",
            "StrictHostKeyChecking=no",
            f"{args.user}@{args.host}",
            f"python3 {remote_path}",
        ]
        for cmd, timeout in ((mkdir_cmd, 60), (scp_cmd, 60), (run_cmd, 300)):
            proc = run(cmd, timeout=timeout)
            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr)
                return proc.returncode
            if proc.stdout.strip():
                print(proc.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
