import json
import re
import urllib.request
from copy import deepcopy
from datetime import datetime

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
WID = "i6T6ke3ltKNQzaCl"


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
backup_name = f"clean_02_approval_backup_phase3a_dryrun_{ts}.json"
with open(backup_name, "w", encoding="utf-8") as f:
    json.dump(wf, f, ensure_ascii=False, indent=2)

nodes = wf["nodes"]
connections = wf.get("connections", {})

nodes = [n for n in nodes if n.get("name") not in {"Phase 3A Dry Run Webhook", "Phase 3A Queue Scanner Dry Run"}]
connections.pop("Phase 3A Dry Run Webhook", None)
connections.pop("Phase 3A Queue Scanner Dry Run", None)

webhook_node = {
    "id": "phase3a-dry-run-webhook",
    "name": "Phase 3A Dry Run Webhook",
    "type": "n8n-nodes-base.webhook",
    "typeVersion": 2,
    "position": [240, 760],
    "parameters": {
        "path": "clean_02_phase3a_dry_run",
        "httpMethod": "POST",
        "responseMode": "lastNode",
        "options": {},
    },
    "webhookId": "phase3a-dry-run-clean-02-approval",
}

scanner_code = r"""
const first = $input.first();
const input = first && first.json && typeof first.json === 'object' ? first.json : {};
const body = input.body && typeof input.body === 'object' ? input.body : input;

const store = $getWorkflowStaticData('global');
store.daily_publish_queue = store.daily_publish_queue && typeof store.daily_publish_queue === 'object' ? store.daily_publish_queue : {};
store.daily_deleted_items = store.daily_deleted_items && typeof store.daily_deleted_items === 'object' ? store.daily_deleted_items : {};

const diagnosticItems = Array.isArray(body.phase3a_diagnostic_items) ? body.phase3a_diagnostic_items : [];
const diagnosticDeleted = body.phase3a_diagnostic_deleted_items && typeof body.phase3a_diagnostic_deleted_items === 'object'
  ? body.phase3a_diagnostic_deleted_items
  : {};
const useDiagnosticInput = diagnosticItems.length > 0;

const queue = useDiagnosticInput
  ? Object.fromEntries(diagnosticItems.map((item, idx) => [String(item.test_id || `diagnostic-${idx + 1}`), item]))
  : store.daily_publish_queue;
const deletedItems = useDiagnosticInput ? diagnosticDeleted : store.daily_deleted_items;

const nowSeoul = body.now_override
  ? new Date(String(body.now_override))
  : new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
const todayKey = `${nowSeoul.getFullYear()}-${String(nowSeoul.getMonth() + 1).padStart(2, '0')}-${String(nowSeoul.getDate()).padStart(2, '0')}`;
const nowMinutes = nowSeoul.getHours() * 60 + nowSeoul.getMinutes();

function parseTimeMinutes(value) {
  const s = String(value || '').trim();
  const m = s.match(/^(\d{1,2}):(\d{2})$/);
  if (!m) return null;
  const hh = Number(m[1]);
  const mm = Number(m[2]);
  if (!Number.isFinite(hh) || !Number.isFinite(mm) || hh < 0 || hh > 23 || mm < 0 || mm > 59) return null;
  return hh * 60 + mm;
}

const summary = {
  mode: useDiagnosticInput ? 'diagnostic_input' : 'staticData',
  dry_run_only: true,
  now_kst: nowSeoul.toISOString(),
  today_key: todayKey,
  actual_static_queue_count: Object.keys(store.daily_publish_queue || {}).length,
  total_queue_count: 0,
  due_count: 0,
  would_publish_count: 0,
  would_publish_reels: 0,
  would_publish_carousels: 0,
  would_publish_feeds: 0,
  skipped_deleted_count: 0,
  skipped_pending_or_missing_count: 0,
  skipped_not_due_count: 0,
  skipped_already_done_count: 0,
  skipped_failed_or_blocked_count: 0,
  items: [],
};

for (const [testId, rawItem] of Object.entries(queue || {})) {
  const item = rawItem && typeof rawItem === 'object' ? rawItem : {};
  const postType = String(item.post_type || item.type || '').trim();
  const status = String(item.status || '').trim();
  const publishStatus = String(item.publish_status || '').trim().toLowerCase();
  const plannedTime = String(item.planned_publish_time || '').trim();
  const plannedMinutes = parseTimeMinutes(plannedTime);
  const isDeleted = status === 'deleted' || Boolean(deletedItems[testId]);

  const decision = {
    test_id: String(item.test_id || testId),
    post_type: postType,
    status,
    publish_status: publishStatus,
    planned_publish_time: plannedTime,
    decision: 'would_skip',
    would_skip_reason: '',
  };

  summary.total_queue_count += 1;

  if (isDeleted) {
    decision.would_skip_reason = 'deleted';
    summary.skipped_deleted_count += 1;
    summary.items.push(decision);
    continue;
  }

  if (status !== 'queued' || !postType || plannedMinutes === null) {
    decision.would_skip_reason = status !== 'queued' ? 'not_queued' : (!postType ? 'post_type_missing' : 'planned_publish_time_missing_or_invalid');
    summary.skipped_pending_or_missing_count += 1;
    summary.items.push(decision);
    continue;
  }

  if (publishStatus === 'published') {
    decision.would_skip_reason = 'already_published';
    summary.skipped_already_done_count += 1;
    summary.items.push(decision);
    continue;
  }

  if (publishStatus === 'failed' || publishStatus === 'blocked') {
    decision.would_skip_reason = `already_${publishStatus}`;
    summary.skipped_failed_or_blocked_count += 1;
    summary.items.push(decision);
    continue;
  }

  if (plannedMinutes > nowMinutes) {
    decision.would_skip_reason = 'not_due_yet';
    summary.skipped_not_due_count += 1;
    summary.items.push(decision);
    continue;
  }

  summary.due_count += 1;

  if (postType === 'reel') {
    if (!/^https?:\/\//i.test(String(item.video_url || ''))) {
      decision.would_skip_reason = 'reel_asset_missing';
      summary.skipped_pending_or_missing_count += 1;
    } else {
      decision.decision = 'would_publish';
      decision.would_skip_reason = '';
      summary.would_publish_count += 1;
      summary.would_publish_reels += 1;
    }
  } else if (postType === 'carousel') {
    const media = Array.isArray(item.carousel?.media) ? item.carousel.media : [];
    const hasPair = Boolean(item.paired_reel_test_id || item.paired_reel_slot || item.publish_after_reel_success);
    if (!hasPair) {
      decision.would_skip_reason = 'carousel_pairing_missing';
      summary.skipped_pending_or_missing_count += 1;
    } else if (media.length < 2 || media.length > 10) {
      decision.would_skip_reason = 'carousel_media_missing_or_invalid';
      summary.skipped_pending_or_missing_count += 1;
    } else {
      decision.decision = 'would_publish';
      decision.would_skip_reason = '';
      summary.would_publish_count += 1;
      summary.would_publish_carousels += 1;
    }
  } else if (postType === 'feed') {
    if (!String(item.caption || '').trim()) {
      decision.would_skip_reason = 'feed_caption_missing';
      summary.skipped_pending_or_missing_count += 1;
    } else if (!/^https?:\/\//i.test(String(item.image_url || item.media_url || ''))) {
      decision.would_skip_reason = 'feed_asset_missing';
      summary.skipped_pending_or_missing_count += 1;
    } else {
      decision.decision = 'would_publish';
      decision.would_skip_reason = '';
      summary.would_publish_count += 1;
      summary.would_publish_feeds += 1;
    }
  } else {
    decision.would_skip_reason = 'unknown_post_type';
    summary.skipped_pending_or_missing_count += 1;
  }

  summary.items.push(decision);
}

store.last_scheduler_dry_run_at = new Date().toISOString();
store.last_scheduler_dry_run_summary = {
  mode: summary.mode,
  total_queue_count: summary.total_queue_count,
  due_count: summary.due_count,
  would_publish_count: summary.would_publish_count,
  skipped_deleted_count: summary.skipped_deleted_count,
  skipped_not_due_count: summary.skipped_not_due_count,
};

return [{ json: summary }];
"""

scanner_node = {
    "id": "phase3a-queue-scanner-dry-run",
    "name": "Phase 3A Queue Scanner Dry Run",
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [520, 760],
    "parameters": {"jsCode": scanner_code.strip()},
}

nodes.extend([webhook_node, scanner_node])
connections["Phase 3A Dry Run Webhook"] = {
    "main": [[{"node": "Phase 3A Queue Scanner Dry Run", "type": "main", "index": 0}]]
}

body = {
    "name": wf["name"],
    "nodes": nodes,
    "connections": connections,
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
updated = req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({
    "backup": backup_name,
    "workflow": updated.get("name"),
    "added_nodes": ["Phase 3A Dry Run Webhook", "Phase 3A Queue Scanner Dry Run"],
    "path": "clean_02_phase3a_dry_run",
}, ensure_ascii=False, indent=2))
