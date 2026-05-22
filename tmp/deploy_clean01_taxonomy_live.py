from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(
    r"C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\01_planning"
)
EXECUTION_ROOT = ROOT.parent / "02_execution"
API_SOURCE = EXECUTION_ROOT / "archive" / "scripts" / "update_build_node_only.py"
BASE_URL = "http://43.201.227.194:5678/api/v1"
WORKFLOW_ID = "KPa5tncCc87z2ZsE"
TARGET_NODE = "Build Simulation Content"
SOURCE_ENGINE = ROOT / "templates" / "clean01_consumer_growth_engine_v4.js"


def fail(message: str, code: int = 1) -> None:
    print(json.dumps({"status": "FAIL", "error": message}, ensure_ascii=False))
    sys.exit(code)


def read_api_key() -> str:
    text = API_SOURCE.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'\bAPI_KEY\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        match = re.search(r'\bAPI\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        fail("n8n API key source was not found")
    return match.group(1)


def request_json(method: str, path: str, api_key: str, payload=None):
    data = None
    headers = {"X-N8N-API-KEY": api_key, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE_URL + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1000]
        fail(f"HTTP {exc.code}: {detail}")
    except Exception as exc:
        fail(str(exc))


def extract_existing_chat_id(js_code: str) -> str | None:
    patterns = [
        r'chatId\s*=\s*String\([^)]*\|\|\s*["\'](\d{6,})["\']\)',
        r'["\'](\d{6,})["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, js_code)
        if match and match.groups():
            return match.group(1)
    return None


def make_live_engine(source: str, current_js: str) -> str:
    chat_id = extract_existing_chat_id(current_js)
    live = source
    live = live.replace(
        'const DEPLOYMENT_STAGE = "draft_preview_only";',
        'const DEPLOYMENT_STAGE = "live_preview_candidates";',
    )
    live = live.replace("simulation_mode: true,", "simulation_mode: false,")
    live = live.replace("preview_only: true,", "preview_only: false,")
    live = live.replace("publish_ready: false,", "publish_ready: true,")
    if chat_id:
        live = live.replace("REPLACE_WITH_EXISTING_CHAT_ID_FROM_CURRENT_WORKFLOW", chat_id)
    return live


def main() -> None:
    api_key = read_api_key()
    workflow = request_json("GET", f"/workflows/{WORKFLOW_ID}", api_key)
    if workflow.get("name") != "clean_01_generator":
        fail(f"unexpected workflow name: {workflow.get('name')}")
    nodes = workflow.get("nodes") or []
    target = next((node for node in nodes if node.get("name") == TARGET_NODE), None)
    if not target:
        fail(f"target node not found: {TARGET_NODE}")
    params = target.setdefault("parameters", {})
    current_js = params.get("jsCode") or params.get("functionCode") or ""
    if not current_js.strip():
        fail("target node has no JavaScript code parameter")

    source = SOURCE_ENGINE.read_text(encoding="utf-8")
    live_engine = make_live_engine(source, current_js)
    required_markers = [
        "YUNA_PRODUCT_TAXONOMY_VERSION",
        "YUNA_PRODUCT_CATEGORY_MIX_RATIO",
        "disposable_device",
        "disposable_cartridge",
        "live_preview_candidates",
    ]
    missing = [marker for marker in required_markers if marker not in live_engine]
    if missing:
        fail(f"live engine missing markers: {missing}")

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"clean_01_generator_pre_taxonomy_mix_{stamp}.json"
    backup_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")

    draft_dir = ROOT / "workflow_drafts" / "live_consumer_growth"
    draft_dir.mkdir(parents=True, exist_ok=True)
    live_engine_path = draft_dir / f"Build_Simulation_Content_taxonomy_mix_live_{stamp}.js"
    live_engine_path.write_text(live_engine, encoding="utf-8")

    before_hash = hashlib.sha256(current_js.encode("utf-8")).hexdigest()
    after_hash = hashlib.sha256(live_engine.encode("utf-8")).hexdigest()
    params["jsCode"] = live_engine

    # n8n v1 rejects several read-only/settings properties when echoed back.
    # Send only the mutable graph body and preserve static/pin data when present.
    body = {
        "name": workflow["name"],
        "nodes": nodes,
        "connections": workflow.get("connections", {}),
        "settings": {
            "executionOrder": (workflow.get("settings") or {}).get("executionOrder", "v1"),
        },
    }
    for key in ("staticData", "pinData"):
        if key in workflow:
            body[key] = workflow[key]

    updated = request_json("PUT", f"/workflows/{WORKFLOW_ID}", api_key, body)
    verified = request_json("GET", f"/workflows/{WORKFLOW_ID}", api_key)
    verified_nodes = verified.get("nodes") or []
    verified_target = next((node for node in verified_nodes if node.get("name") == TARGET_NODE), None)
    verified_js = ((verified_target or {}).get("parameters") or {}).get("jsCode", "")
    if hashlib.sha256(verified_js.encode("utf-8")).hexdigest() != after_hash:
        fail("deployed code hash did not verify")
    if len(verified_nodes) != len(nodes):
        fail("node count changed unexpectedly")

    report_dir = ROOT / "reports" / "deployments"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"clean01_yuna_taxonomy_mix_live_deploy_{stamp}.md"
    report_path.write_text(
        "\n".join(
            [
                "# clean_01_generator YUNA Product Taxonomy Mix Live Deploy",
                "",
                f"- timestamp: {stamp}",
                f"- workflow_id: {WORKFLOW_ID}",
                f"- workflow_name: {workflow.get('name')}",
                f"- target_node: {TARGET_NODE}",
                f"- active_before: {workflow.get('active')}",
                f"- active_after: {verified.get('active')}",
                f"- active_version_id: {verified.get('activeVersionId')}",
                f"- nodes_before: {len(nodes)}",
                f"- nodes_after: {len(verified_nodes)}",
                f"- code_sha256_before: {before_hash}",
                f"- code_sha256_after: {after_hash}",
                f"- backup_path: {backup_path}",
                f"- live_engine_path: {live_engine_path}",
                "- changed_surface: target node jsCode only",
                "- product_mix_ratio: device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3",
                "- instagram_publish_call: none",
                "- credential_output: none",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    telemetry_dir = ROOT / "telemetry"
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = telemetry_dir / f"clean01_yuna_taxonomy_mix_live_deploy_{stamp}.json"
    telemetry_path.write_text(
        json.dumps(
            {
                "status": "PASS",
                "timestamp": stamp,
                "workflow_id": WORKFLOW_ID,
                "target_node": TARGET_NODE,
                "active_after": verified.get("active"),
                "active_version_id": verified.get("activeVersionId"),
                "nodes_after": len(verified_nodes),
                "code_sha256_before": before_hash,
                "code_sha256_after": after_hash,
                "backup_path": str(backup_path),
                "live_engine_path": str(live_engine_path),
                "report_path": str(report_path),
                "updated_version_id": updated.get("versionId"),
                "product_mix_ratio": "device:1,e_liquid:10,disposable_device:7,disposable_cartridge:3",
                "instagram_publish_call": False,
                "credential_output": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "PASS",
                "workflow": workflow.get("name"),
                "workflow_id": WORKFLOW_ID,
                "target_node": TARGET_NODE,
                "active_after": verified.get("active"),
                "active_version_id": verified.get("activeVersionId"),
                "backup_path": str(backup_path),
                "live_engine_path": str(live_engine_path),
                "report_path": str(report_path),
                "telemetry_path": str(telemetry_path),
                "code_sha256_after": after_hash,
                "updated_version_id": updated.get("versionId"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
