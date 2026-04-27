$path = 'C:\Users\minho\Documents\02_work\03_AI\02_sns_automation\01_instagram\02_execution\workflow_IY3f5KcJDMDgWRJk.json'
$wf = Get-Content -Raw $path | ConvertFrom-Json

$build = $wf.nodes | Where-Object { $_.name -eq 'Build DMQVD Detail Message' } | Select-Object -First 1
if (-not $build) { throw 'Missing node: Build DMQVD Detail Message' }

$build.parameters.jsCode = @'
const rows = $input.all().map(i => i.json || {});
const r = rows.slice().sort((a, b) => new Date(b.last_signal_at || b.last_queued_at || b.first_queued_at || 0).getTime() - new Date(a.last_signal_at || a.last_queued_at || a.first_queued_at || 0).getTime())[0] || {};
if (!r.user_id) return [];
const latest = String(r.latest_message || '').trim();
const lines = [
  '🔎 DM Queue Detail',
  `- user: ${String(r.user_display_name || r.user_id || '').trim()}`,
  `- owner: ${String(r.operator_owner || '').trim() || '-'}`,
  `- queue_status: ${String(r.queue_status || '').trim() || '-'}`,
  `- review_status: ${String(r.review_status || '').trim() || '-'}`,
  `- lead_type: ${String(r.lead_type || '').trim() || '-'}`,
  `- review_priority: ${String(r.review_priority || '').trim() || '-'}`,
  `- bucket: ${String(r.queue_bucket || '').trim() || '-'}`,
  `- reason: ${String(r.review_reason || '').trim() || '-'}`,
  `- health: ${String(r.dm_health_status || '').trim() || '-'}`,
  `- followup: ${String(r.followup_status || '').trim() || '-'} / ${String(r.next_followup_at || '').trim() || '-'}`,
  `- snapshot: ${String(r.operator_snapshot || '').trim() || '-'}`,
  `- hint: ${String(r.next_action_hint || '').trim() || '-'}`,
  `- today: ${String(r.operator_today_hint || '').trim() || '-'}`
];
if (latest) lines.push('', 'latest:', latest);
const extras = [];
if (String(r.last_operator_action || '').trim()) extras.push(`last_action: ${String(r.last_operator_action || '').trim()}`);
if (String(r.dm_last_triggered_replies || '').trim()) extras.push(`sent: ${String(r.dm_last_triggered_replies || '').trim()}`);
if (String(r.dm_last_blocked_replies || '').trim()) extras.push(`blocked: ${String(r.dm_last_blocked_replies || '').trim()}`);
if (extras.length) lines.push('', extras.join(' | '));

const keyboard = [
  [
    { text: 'In Review', callback_data: `dmq|in_review|${r.user_id}` },
    { text: 'Resolved', callback_data: `dmq|resolved|${r.user_id}` },
    { text: 'Archive', callback_data: `dmq|archive|${r.user_id}` },
    { text: 'Reopen', callback_data: `dmq|reopen|${r.user_id}` }
  ],
  [
    { text: 'Claim', callback_data: `dmqm|claim|${r.user_id}` },
    { text: 'FU Today', callback_data: `dmqm|fu_today|${r.user_id}` },
    { text: 'FU Tomorrow', callback_data: `dmqm|fu_tomorrow|${r.user_id}` }
  ],
  [
    { text: 'FU Done', callback_data: `dmqm|fu_done|${r.user_id}` },
    { text: 'Clear FU', callback_data: `dmqm|fu_clear|${r.user_id}` }
  ],
  [
    { text: 'Must Handle', callback_data: 'dmqv|must_handle' },
    { text: 'My Open', callback_data: 'dmqv|my_open' }
  ]
];

return [{
  json: {
    admin_chat_id: String(r.admin_chat_id || '7592247598'),
    dmqvd_detail_text: lines.join('\n'),
    reply_markup: JSON.stringify({ inline_keyboard: keyboard })
  }
}];
'@

$send = $wf.nodes | Where-Object { $_.name -eq 'Send DMQVD Detail Telegram' } | Select-Object -First 1
if (-not $send) { throw 'Missing node: Send DMQVD Detail Telegram' }

$send.parameters.bodyParameters.parameters = @(
  [pscustomobject]@{ name = 'chat_id'; value = '={{$json.admin_chat_id || $json.callback_chat_id || "7592247598"}}' },
  [pscustomobject]@{ name = 'text'; value = '={{$json.dmqvd_detail_text}}' },
  [pscustomobject]@{ name = 'reply_markup'; value = '={{$json.reply_markup}}' }
)

($wf | ConvertTo-Json -Depth 100) | Set-Content -Path $path -Encoding utf8
