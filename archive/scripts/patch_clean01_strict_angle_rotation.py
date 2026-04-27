import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = "http://43.201.227.194:5678"
WID = "KPa5tncCc87z2ZsE"
API = re.search(
    r'API = "([^"]+)"',
    Path("add_reel_pipeline_minimal.py").read_text(encoding="utf-8"),
).group(1)


def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=60) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def put_workflow(wf):
    body = {
        "name": wf["name"],
        "nodes": wf["nodes"],
        "connections": wf.get("connections", {}),
        "settings": wf.get("settings", {}),
        "staticData": wf.get("staticData", {}),
        "pinData": wf.get("pinData", {}),
    }
    if wf.get("meta") is not None:
        body["meta"] = wf["meta"]
    return req(f"/api/v1/workflows/{wf['id']}", "PUT", body)


wf = req(f"/api/v1/workflows/{WID}")
backup = f"clean_01_generator_backup_strict_angle_rotation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
Path(backup).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")
node = next(n for n in wf["nodes"] if n.get("name") == "Build Simulation Content")
params = node["parameters"]
code = params.get("jsCode") or params.get("code")
key = "jsCode" if "jsCode" in params else "code"

old = "  const dominantAngle = pickRotated(psychAngles, idx, `${seed}_${slot.post_type}`, \"\");"
new = "  const dominantAngle = slot.psych_angle_override || pickRotated(psychAngles, idx, `${seed}_${slot.post_type}`, \"\");"
if old not in code:
    raise RuntimeError("dominantAngle line not found")
code = code.replace(old, new, 1)

old_map = "  const psych = buildPsychPost(f, slot, idx, executionSeed);"
new_map = """  const angleOffset = Math.abs(String(executionSeed || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0)) % psychAngles.length;
  const slotForPsych = { ...slot, psych_angle_override: psychAngles[(idx + angleOffset) % psychAngles.length] };
  const psych = buildPsychPost(f, slotForPsych, idx, executionSeed);"""
if old_map not in code:
    raise RuntimeError("psych build line not found")
code = code.replace(old_map, new_map, 1)

params[key] = code
put_workflow(wf)
print(json.dumps({"backup": backup, "patched": True}, ensure_ascii=False, indent=2))
