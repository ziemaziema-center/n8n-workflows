from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def load_task(raw: str) -> dict[str, Any]:
    return json.loads(raw)


def read_report(path: Path) -> str:
    if not path.exists():
        return "작업 보고서 파일을 찾지 못했습니다."
    return path.read_text(encoding="utf-8", errors="replace")[:3000]


CHAT_ID_PATTERN = re.compile(r'("chat_id"\s*:\s*")-?\d{6,20}(")')
ESCAPED_CHAT_ID_PATTERN = re.compile(r'(\\"chat_id\\"\s*:\s*\\")-?\d{6,20}(\\" )'.replace(" ", ""))


def redact_response_body(value: str) -> str:
    value = CHAT_ID_PATTERN.sub(r'\1REDACTED_CHAT_ID\2', value)
    value = ESCAPED_CHAT_ID_PATTERN.sub(r'\1REDACTED_CHAT_ID\2', value)
    return value


def notify(task: dict[str, Any], report_path: Path, log_path: Path, status: str) -> dict[str, Any]:
    notification = task.get("notification") if isinstance(task.get("notification"), dict) else {}
    webhook_url = str(notification.get("webhook_url") or "").strip()
    chat_id = str(notification.get("chat_id") or "").strip()
    if not webhook_url or not chat_id:
        return {"status": "SKIPPED", "reason": "notification webhook or chat_id missing"}
    summary = "\n".join(
        [
            f"결론: {'완료' if status == 'PASS' else '확인 필요'}",
            f"작업번호: {task.get('task_id', 'unknown')}",
            "",
            "완료 보고:",
            read_report(report_path),
            "",
            f"로그 위치: {log_path}",
        ]
    )
    payload = {
        "action": "notify",
        "chat_id": chat_id,
        "task_id": task.get("task_id"),
        "status": status,
        "summary": summary,
    }
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"status": "PASS", "http_status": response.status, "body_tail": redact_response_body(body[-1000:])}
    except urllib.error.URLError as exc:
        return {"status": "FAIL", "reason": str(exc)}


def main() -> int:
    if len(sys.argv) < 5:
        print(json.dumps({"status": "FAIL", "reason": "usage: task_json report_path log_path status"}))
        return 2
    result = notify(load_task(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"PASS", "SKIPPED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
