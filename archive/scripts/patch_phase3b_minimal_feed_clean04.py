import json
import re
import urllib.request
from datetime import datetime

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
W2 = "i6T6ke3ltKNQzaCl"
W4 = "w9e3wiyca6qZUS4r"


def req(path, method="GET", payload=None):
    data = None
    headers = {"X-N8N-API-KEY": API}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=headers)
    with urllib.request.urlopen(r, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backups = []

wf2 = req(f"/api/v1/workflows/{W2}")
b2 = f"clean_02_approval_backup_phase3b_feed_queue_{ts}.json"
with open(b2, "w", encoding="utf-8") as f:
    json.dump(wf2, f, ensure_ascii=False, indent=2)
backups.append(b2)

n = next(x for x in wf2["nodes"] if x.get("name") == "Normalize Callback")
code = n["parameters"]["jsCode"]
code = code.replace(
    "    hook: String(body.hook || '').trim(),\n    updated_at: new Date().toISOString(),",
    "    hook: String(body.hook || '').trim(),\n    image_url: String(body.image_url || body.media_url || '').trim(),\n    media_url: String(body.media_url || body.image_url || '').trim(),\n    updated_at: new Date().toISOString(),",
)
code = code.replace(
    "  const videoUrl = String(reelMap[testId] || '').trim();\n",
    "  const videoUrl = String(reelMap[testId] || '').trim();\n  const feedImageUrl = String(feedPayload?.image_url || feedPayload?.media_url || '').trim();\n",
)
code = code.replace(
    "    video_url: typeFromAction === 'reel' ? videoUrl : '',\n    carousel: typeFromAction === 'carousel' ? {",
    "    video_url: typeFromAction === 'reel' ? videoUrl : '',\n    image_url: typeFromAction === 'feed' ? feedImageUrl : '',\n    media_url: typeFromAction === 'feed' ? feedImageUrl : '',\n    carousel: typeFromAction === 'carousel' ? {",
)
n["parameters"]["jsCode"] = code
body2 = {
    "name": wf2["name"],
    "nodes": wf2["nodes"],
    "connections": wf2.get("connections", {}),
    "settings": wf2.get("settings", {}),
    "staticData": wf2.get("staticData", {}),
    "pinData": wf2.get("pinData", {}),
}
req(f"/api/v1/workflows/{W2}", "PUT", body2)

wf4 = req(f"/api/v1/workflows/{W4}")
b4 = f"clean_04_carousel_publisher_backup_phase3b_publish_node_{ts}.json"
with open(b4, "w", encoding="utf-8") as f:
    json.dump(wf4, f, ensure_ascii=False, indent=2)
backups.append(b4)

pub = next(x for x in wf4["nodes"] if x.get("name") == "IG Publish Carousel")
# Preserve existing token expression/value while matching the working Reel publish node's form-urlencoded shape.
old_body = pub.get("parameters", {}).get("jsonBody", "")
token_match = re.search(r'access_token\\?":\\?\s*\\?"([^"}]+)', old_body)
token = token_match.group(1) if token_match else ""
if not token:
    token_match = re.search(r'access_token:\s*"([^"]+)"', old_body)
    token = token_match.group(1) if token_match else ""
pub["parameters"] = {
    "method": "POST",
    "url": "https://graph.facebook.com/v23.0/17841436538210981/media_publish",
    "sendBody": True,
    "contentType": "form-urlencoded",
    "specifyBody": "keypair",
    "bodyParameters": {
        "parameters": [
            {"name": "creation_id", "value": "={{$json.id}}"},
            {"name": "access_token", "value": token},
        ]
    },
    "options": {},
}

body4 = {
    "name": wf4["name"],
    "nodes": wf4["nodes"],
    "connections": wf4.get("connections", {}),
    "settings": wf4.get("settings", {}),
    "staticData": wf4.get("staticData", {}),
    "pinData": wf4.get("pinData", {}),
}
req(f"/api/v1/workflows/{W4}", "PUT", body4)

print(json.dumps({"backups": backups, "modified": {"clean_02_approval": ["Normalize Callback"], "clean_04_carousel_publisher": ["IG Publish Carousel"]}}, ensure_ascii=False, indent=2))
