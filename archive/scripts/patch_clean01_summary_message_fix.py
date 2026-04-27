import json
import re
import urllib.request
from datetime import datetime

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
WID = "KPa5tncCc87z2ZsE"


def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


wf = req(f"/api/v1/workflows/{WID}")
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_name = f"clean_01_generator_backup_summary_message_fix_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

node = next(n for n in wf["nodes"] if n.get("name") == "Telegram Duplicate Summary")
for p in node["parameters"]["bodyParameters"]["parameters"]:
    if p.get("name") == "chat_id":
        p["value"] = "={{$json.chat_id || '7592247598'}}"
    if p.get("name") == "text":
        p["value"] = "={{ '[PREVIEW SUMMARY]\\n오늘 생성 후보: ' + (($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).total_candidates || 0) + '개\\nTelegram 전송됨: ' + (($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).sent_candidates || 0) + '개\\nduplicate_blocked: ' + (($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).blocked_count || 0) + '개\\nneeds_manual_review: ' + (($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).manual_review_count || 0) + '개\\n\\n[BLOCKED]\\n' + (((($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).blocked_items || []).map(x => '- ' + x.post_type + ' / ' + x.test_id + ' / ' + (x.blocked_reason || '')).join('\\n')) || '없음') + '\\n\\n[MANUAL REVIEW]\\n' + (((($getWorkflowStaticData(\"global\").last_duplicate_block_summary || {}).manual_review_items || []).map(x => '- ' + x.post_type + ' / ' + x.test_id + ' / ' + (x.warning_reason || '')).join('\\n')) || '없음') }}"

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({"backup": backup_name, "workflow": "clean_01_generator", "node": "Telegram Duplicate Summary"}, ensure_ascii=False, indent=2))
