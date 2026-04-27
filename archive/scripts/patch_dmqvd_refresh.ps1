$path = 'C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\02_execution\workflow_IY3f5KcJDMDgWRJk.json'
$wf = Get-Content -Raw $path | ConvertFrom-Json

function Get-Node {
  param([string]$Name)
  $node = $wf.nodes | Where-Object { $_.name -eq $Name } | Select-Object -First 1
  if (-not $node) { throw "Missing node: $Name" }
  return $node
}

function Ensure-Conn {
  param([string]$Name, $Value)
  if ($wf.connections.PSObject.Properties.Name -contains $Name) {
    $wf.connections.$Name = $Value
  } else {
    $wf.connections | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
  }
}

$parse = Get-Node 'Parse Callback'
$parse.parameters.jsCode = @'
const body = $json.body || $json;
const callback = body.callback_query || null;
const message = body.message || body.edited_message || body.channel_post || null;
const isCallback = !!callback;
const isMessage = !!message;
const actionData = String(callback?.data || "");
const parts = actionData.split("|");
const action = String(parts[0] || "");
const subAction = String(parts[1] || "");
const targetId = String(parts.slice(2).join("|") || "");
const chat = callback?.message?.chat || message?.chat || {};
const user = callback?.from || message?.from || {};
const callbackText = String(callback?.message?.text || callback?.message?.caption || "");
const messageText = String(message?.text || message?.caption || "").trim();
const isDmq = action === 'dmq';
const isDmqm = action === 'dmqm';
const isDmqv = action === 'dmqv';
const isDmqvd = action === 'dmqvd';
const callbackOrigin = isDmqvd
  ? 'detail'
  : /DM Queue Detail/i.test(callbackText)
    ? 'detail'
    : /DM Queue View:/i.test(callbackText)
      ? 'view'
      : /Top DM Picks Today/i.test(callbackText)
        ? 'top_picks'
        : isCallback
          ? 'other'
          : 'unknown';

return {
  json: {
    event_type: isCallback ? "callback_query" : (isMessage ? "message" : "unknown"),
    action: isCallback ? action : "dm_inbound",
    content_key: isCallback ? (isDmq || isDmqm || isDmqv || isDmqvd ? targetId : subAction) : "",
    callback_id: callback?.id || "",
    callback_message_id: callback?.message?.message_id || "",
    callback_caption: callback?.message?.caption || "",
    callback_message_text: callbackText,
    callback_origin: callbackOrigin,
    chat_id: String(chat?.id || "7592247598"),
    user_id: String(user?.id || chat?.id || "7592247598"),
    username: user?.username || chat?.username || "",
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    message_id: message?.message_id || callback?.message?.message_id || "",
    message_text: messageText,
    dmq_action: isDmq ? subAction : "",
    dmq_user_id: isDmq ? targetId : "",
    dmq_callback: isDmq,
    dmqm_action: isDmqm ? subAction : "",
    dmqm_user_id: isDmqm ? targetId : "",
    dmqm_callback: isDmqm,
    dmqv_action: isDmqv ? subAction : "",
    dmqv_user_id: isDmqv ? targetId : "",
    dmqv_callback: isDmqv,
    dmqvd_user_id: isDmqvd ? targetId : "",
    dmqvd_callback: isDmqvd,
    raw: body
  }
};
'@

$lookupDMQ = Get-Node 'Build DMQ Operator Lookup'
$lookupDMQ.parameters.jsCode = @'
const p = $items("Parse Callback", 0, 0)[0]?.json || {};
const targetUserId = String(p.dmq_user_id || '').trim();
if (!targetUserId) return [];
return [{
  json: {
    user_id: targetUserId,
    dmq_callback: true,
    dmq_action: String(p.dmq_action || '').trim(),
    admin_chat_id: String(p.chat_id || '7592247598'),
    callback_chat_id: String(p.chat_id || '7592247598'),
    callback_message_id: String(p.callback_message_id || ''),
    callback_id: String(p.callback_id || ''),
    callback_origin: String(p.callback_origin || ''),
    operator_user_id: String(p.user_id || ''),
    operator_username: String(p.username || ''),
    operator_first_name: String(p.first_name || ''),
    operator_last_name: String(p.last_name || ''),
    operator_display_name: String(p.first_name || p.username || p.user_id || '').trim() || String(p.user_id || '').trim(),
    dmq_operator_detail_refresh: String(p.callback_origin || '') === 'detail' ? 'true' : 'false'
  }
}];
'@

$updateDMQ = Get-Node 'Build DMQ Operator Update'
$updateDMQ.parameters.jsCode = @'
const lookup = $items("Build DMQ Operator Lookup", 0, 0)[0]?.json || {};
const rows = $input.all().map(i => i.json).filter(r => String(r.user_id || '') === String(lookup.user_id || ''));
const existing = rows.slice().sort((a, b) => new Date(a.last_queued_at || a.first_queued_at || 0).getTime() - new Date(b.last_queued_at || b.first_queued_at || 0).getTime()).slice(-1)[0] || {};
const now = new Date().toISOString();
const action = String(lookup.dmq_action || '').trim();
if (!String(lookup.user_id || '').trim() || !action) return [];

const out = {
  ...existing,
  user_id: String(lookup.user_id || '').trim(),
  user_display_name: String(existing.user_display_name || existing.username || lookup.user_id || '').trim() || String(lookup.user_id || '').trim(),
  review_status: String(existing.review_status || '').trim() || 'pending',
  queue_status: String(existing.queue_status || '').trim() || 'open',
  operator_note: String(existing.operator_note || '').trim(),
  operator_owner: String(existing.operator_owner || '').trim(),
  next_followup_at: String(existing.next_followup_at || '').trim(),
  followup_status: String(existing.followup_status || '').trim() || 'none',
  last_operator_action: action,
  last_operator_action_at: now,
  review_reason: String(existing.review_reason || 'review').trim() || 'review',
  reopen_reason: String(existing.reopen_reason || 'none').trim() || 'none',
  admin_chat_id: String(lookup.admin_chat_id || lookup.callback_chat_id || '7592247598'),
  callback_chat_id: String(lookup.callback_chat_id || lookup.admin_chat_id || '7592247598'),
  callback_message_id: String(lookup.callback_message_id || ''),
  callback_id: String(lookup.callback_id || ''),
  callback_origin: String(lookup.callback_origin || ''),
  dmq_operator_detail_refresh: String(lookup.dmq_operator_detail_refresh || 'false'),
  dmq_operator_action: action,
  dmq_operator_confirm_status: action,
  dmq_operator_confirm_queue_status: String(existing.queue_status || '').trim() || 'open',
  dmq_operator_confirm_text: ''
};

if (action === 'in_review') {
  out.review_status = 'in_review';
} else if (action === 'resolved') {
  out.review_status = 'resolved';
} else if (action === 'archive') {
  out.queue_status = 'archived';
  out.archived_at = now;
  out.archive_reason = 'operator_archive';
  out.dmq_operator_confirm_queue_status = 'archived';
} else if (action === 'reopen') {
  out.queue_status = 'open';
  out.reopen_reason = 'operator_reopen';
  out.dmq_operator_confirm_queue_status = 'open';
}

out.dmq_operator_confirm_review_status = String(out.review_status || 'pending');
out.dmq_operator_confirm_queue_status = String(out.queue_status || 'open');
out.dmq_operator_confirm_text = `🛠 Queue updated
- user: ${out.user_display_name || out.user_id}
- action: ${action}
- review_status: ${out.review_status || 'pending'}
- queue_status: ${out.queue_status || 'open'}`;

return [{ json: out }];
'@

$lookupDMQM = Get-Node 'Build DMQM Operator Lookup'
$lookupDMQM.parameters.jsCode = @'
const p = $items("Parse Callback", 0, 0)[0]?.json || {};
const targetUserId = String(p.dmqm_user_id || '').trim();
if (!targetUserId) return [];
return [{
  json: {
    user_id: targetUserId,
    dmqm_callback: true,
    dmqm_action: String(p.dmqm_action || '').trim(),
    admin_chat_id: String(p.chat_id || '7592247598'),
    callback_chat_id: String(p.chat_id || '7592247598'),
    callback_message_id: String(p.callback_message_id || ''),
    callback_id: String(p.callback_id || ''),
    callback_origin: String(p.callback_origin || ''),
    operator_user_id: String(p.user_id || ''),
    operator_username: String(p.username || ''),
    operator_first_name: String(p.first_name || ''),
    operator_last_name: String(p.last_name || ''),
    operator_display_name: String(p.first_name || p.username || p.user_id || '').trim() || String(p.user_id || '').trim(),
    dmq_operator_detail_refresh: String(p.callback_origin || '') === 'detail' ? 'true' : 'false'
  }
}];
'@

$updateDMQM = Get-Node 'Build DMQM Operator Update'
$updateDMQM.parameters.jsCode = @'
const lookup = $items("Build DMQM Operator Lookup", 0, 0)[0]?.json || {};
const rows = $input.all().map(i => i.json).filter(r => String(r.user_id || '') === String(lookup.user_id || ''));
const existing = rows.slice().sort((a, b) => new Date(a.last_queued_at || a.first_queued_at || 0).getTime() - new Date(b.last_queued_at || b.first_queued_at || 0).getTime()).slice(-1)[0] || {};
const now = new Date().toISOString();
const action = String(lookup.dmqm_action || '').trim();
if (!String(lookup.user_id || '').trim() || !action) return [];

const ownerName = String(lookup.operator_username || lookup.operator_display_name || lookup.operator_first_name || lookup.operator_user_id || '').trim() || String(lookup.user_id || '').trim();
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
tomorrow.setHours(23, 59, 59, 999);
const today = new Date();
today.setHours(23, 59, 59, 999);

const out = {
  ...existing,
  user_id: String(lookup.user_id || '').trim(),
  user_display_name: String(existing.user_display_name || existing.username || lookup.user_id || '').trim() || String(lookup.user_id || '').trim(),
  review_status: String(existing.review_status || '').trim() || 'pending',
  queue_status: String(existing.queue_status || '').trim() || 'open',
  operator_note: String(existing.operator_note || '').trim(),
  operator_owner: String(existing.operator_owner || '').trim(),
  next_followup_at: String(existing.next_followup_at || '').trim(),
  followup_status: String(existing.followup_status || '').trim() || 'none',
  last_operator_action: action,
  last_operator_action_at: now,
  review_reason: String(existing.review_reason || 'review').trim() || 'review',
  reopen_reason: String(existing.reopen_reason || 'none').trim() || 'none',
  admin_chat_id: String(lookup.admin_chat_id || lookup.callback_chat_id || '7592247598'),
  callback_chat_id: String(lookup.callback_chat_id || lookup.admin_chat_id || '7592247598'),
  callback_message_id: String(lookup.callback_message_id || ''),
  callback_id: String(lookup.callback_id || ''),
  callback_origin: String(lookup.callback_origin || ''),
  dmq_operator_detail_refresh: String(lookup.dmq_operator_detail_refresh || 'false'),
  dmq_operator_action: action,
  dmq_operator_confirm_status: action,
  dmq_operator_confirm_queue_status: String(existing.queue_status || '').trim() || 'open',
  dmq_operator_confirm_text: ''
};

if (action === 'claim') {
  out.operator_owner = ownerName;
} else if (action === 'fu_today') {
  out.followup_status = 'scheduled';
  out.next_followup_at = today.toISOString();
} else if (action === 'fu_tomorrow') {
  out.followup_status = 'scheduled';
  out.next_followup_at = tomorrow.toISOString();
} else if (action === 'fu_done') {
  out.followup_status = 'done';
} else if (action === 'fu_clear') {
  out.followup_status = 'none';
  out.next_followup_at = '';
}

out.dmq_operator_confirm_review_status = String(out.review_status || 'pending');
out.dmq_operator_confirm_queue_status = String(out.queue_status || 'open');
out.dmq_operator_confirm_text = `🛠 Queue manager updated
- user: ${out.user_display_name || out.user_id}
- action: ${action}
- owner: ${out.operator_owner || ownerName || out.user_id}
- followup_status: ${out.followup_status || 'none'}
- next_followup_at: ${out.next_followup_at || ''}`;

return [{ json: out }];
'@

$refreshLookup = [pscustomobject]@{
  id = ([guid]::NewGuid().ToString())
  name = 'Build DMQ Detail Refresh Lookup'
  type = 'n8n-nodes-base.code'
  typeVersion = 2
  position = @(-1280, 1120)
  parameters = [pscustomobject]@{
    mode = 'runOnceForEachItem'
    jsCode = @'
const p = $json || {};
const targetUserId = String(p.user_id || '').trim();
if (!targetUserId) return [];
return [{
  json: {
    user_id: targetUserId,
    admin_chat_id: String(p.admin_chat_id || p.callback_chat_id || '7592247598'),
    callback_chat_id: String(p.callback_chat_id || p.admin_chat_id || '7592247598'),
    callback_message_id: String(p.callback_message_id || ''),
    callback_id: String(p.callback_id || ''),
    callback_origin: String(p.callback_origin || ''),
    operator_user_id: String(p.operator_user_id || ''),
    operator_username: String(p.operator_username || ''),
    operator_display_name: String(p.operator_display_name || ''),
    operator_first_name: String(p.operator_first_name || ''),
    operator_last_name: String(p.operator_last_name || '')
  }
}];
'@
  }
}

$refreshRoute = [pscustomobject]@{
  id = ([guid]::NewGuid().ToString())
  name = 'Route DM Detail Refresh'
  type = 'n8n-nodes-base.if'
  typeVersion = 2
  position = @(-560, 640)
  parameters = [pscustomobject]@{
    options = [pscustomobject]@{}
    conditions = [pscustomobject]@{
      options = [pscustomobject]@{ typeValidation = 'strict'; version = 2; leftValue = ''; caseSensitive = $true }
      conditions = @(
        [pscustomobject]@{
          leftValue = '={{$json.dmq_operator_detail_refresh}}'
          rightValue = 'true'
          operator = [pscustomobject]@{ type = 'string'; operation = 'equals' }
        }
      )
      combinator = 'and'
    }
  }
}

$existingNames = @($wf.nodes | ForEach-Object { $_.name })
foreach ($node in @($refreshLookup, $refreshRoute)) {
  if ($existingNames -notcontains $node.name) { $wf.nodes += $node }
}

Ensure-Conn 'Build DMQ Operator Lookup' @(@(@{ node = 'Read DM Review Queue Operator'; type = 'main'; index = 0 }))
Ensure-Conn 'Read DM Review Queue Operator' @(@(@{ node = 'Build DMQ Operator Update'; type = 'main'; index = 0 }))
Ensure-Conn 'Build DMQM Operator Lookup' @(@(@{ node = 'Read DM Review Queue Management'; type = 'main'; index = 0 }))
Ensure-Conn 'Read DM Review Queue Management' @(@(@{ node = 'Build DMQM Operator Update'; type = 'main'; index = 0 }))
Ensure-Conn 'Upsert DM Review Queue' @(@(@{ node = 'Route DM Detail Refresh'; type = 'main'; index = 0 }))
Ensure-Conn 'Route DM Detail Refresh' @(
  @(@{ node = 'Build DMQ Detail Refresh Lookup'; type = 'main'; index = 0 }),
  @(@{ node = 'Route DMQ Operator Confirmation'; type = 'main'; index = 0 })
)
Ensure-Conn 'Build DMQ Detail Refresh Lookup' @(@(@{ node = 'Read DM Review Queue Detail'; type = 'main'; index = 0 }))
Ensure-Conn 'Read DM Review Queue Detail' @(@(@{ node = 'Build DMQVD Detail Message'; type = 'main'; index = 0 }))
Ensure-Conn 'Build DMQVD Detail Message' @(@(@{ node = 'Send DMQVD Detail Telegram'; type = 'main'; index = 0 }))
Ensure-Conn 'Route DMQ Operator Confirmation' @(
  @(@{ node = 'Send DMQ Operator Confirmation Telegram'; type = 'main'; index = 0 }),
  @()
)

($wf | ConvertTo-Json -Depth 100) | Set-Content -Path $path -Encoding utf8
