from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "reports" / "hq_continuation_ledger_2026-05-18.json"
DEFAULT_FINAL_REPORT = ROOT / "reports" / "hq_runtime_orchestration_final_report_2026-05-18.md"
DEFAULT_OUTPUT = ROOT / "runtime" / "reports" / "telegram_summary_preview_2026-05-18.txt"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def bullet_lines(items: list[str], limit: int = 6) -> list[str]:
    shown = items[:limit]
    lines = [f"- {item}" for item in shown]
    if len(items) > limit:
        lines.append(f"- 외 {len(items) - limit}개")
    return lines


def render_summary(ledger: dict, final_report_path: Path) -> str:
    completed = ledger.get("completed_items", [])
    pending = ledger.get("pending_items", [])
    gates = ledger.get("deferred_gates", [])
    next_items = ledger.get("next_executable_subtasks", [])

    gate_names = []
    for gate in gates:
        if isinstance(gate, dict):
            gate_names.append(gate.get("name", "unknown_gate"))
        else:
            gate_names.append(str(gate))

    lines = [
        "[Kindred AI Controller]",
        "상태: 로컬 준비 완료",
        f"작업번호: {ledger.get('task_id', 'unknown')}",
        "",
        "이번에 끝난 일:",
        *bullet_lines(completed),
        "",
        "아직 남은 일:",
        *bullet_lines(pending),
        "",
        "승인받고 따로 확인할 live gate:",
        *bullet_lines(gate_names),
        "",
        "다음에 바로 할 일:",
        *bullet_lines(next_items),
        "",
        "사용 방법:",
        "- 이 메시지는 Telegram 전송 전 미리보기입니다.",
        "- 실제 전송 전에는 live Telegram send gate를 1회만 승인해서 확인합니다.",
        "- 상세 보고서는 아래 파일에 있습니다.",
        f"- {final_report_path.as_posix()}",
        "",
        f"생성시각(UTC): {datetime.now(timezone.utc).isoformat()}",
    ]
    return "\n".join(lines) + "\n"


def write_preview(ledger_path: Path, final_report_path: Path, output_path: Path) -> dict:
    ledger = load_json(ledger_path)
    if not final_report_path.exists():
        raise FileNotFoundError(final_report_path)
    text = render_summary(ledger, final_report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return {
        "ok": True,
        "output_path": str(output_path),
        "characters": len(text),
        "live_telegram_sent": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render TAC ledger into a Korean Telegram preview.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--final-report", type=Path, default=DEFAULT_FINAL_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = write_preview(args.ledger, args.final_report, args.output)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
