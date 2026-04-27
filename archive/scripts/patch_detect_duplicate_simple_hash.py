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


def req(path: str, method: str = "GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=60) as res:
        raw = res.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def put_workflow(wf: dict):
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
backup = f"clean_01_generator_backup_detect_duplicate_simple_hash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
Path(backup).write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")

node = next(n for n in wf["nodes"] if n.get("name") == "Detect Duplicate Content")
params = node.setdefault("parameters", {})
key = "jsCode" if "jsCode" in params else "code"
code = params[key]

if "require('crypto')" in code or 'require("crypto")' in code or "crypto.createHash" in code:
    code = re.sub(r"const\s+crypto\s*=\s*require\(['\"]crypto['\"]\);\s*", "", code)
    code = re.sub(r"crypto\.createHash\([^)]*\)\.update\(([^)]*)\)\.digest\(['\"][^'\"]+['\"]\)", r"simpleHash(\1)", code)

old = re.search(r"function hash\(value\) \{[\s\S]*?\n\}", code)
if not old:
    raise RuntimeError("hash(value) function not found in Detect Duplicate Content")

replacement = """function simpleHash(str) {
  str = String(str || '');
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return String(Math.abs(hash));
}

function hash(value) {
  return simpleHash(value);
}"""

code = code[:old.start()] + replacement + code[old.end():]

if "crypto" in code:
    raise RuntimeError("crypto reference still present after patch")

params[key] = code
put_workflow(wf)
print(json.dumps({"backup": backup, "workflow": wf["name"], "node": node["name"], "patched": True}, ensure_ascii=False, indent=2))
