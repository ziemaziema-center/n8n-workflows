$path = Join-Path $PSScriptRoot 'workflow_01_live.json'
$wf = Get-Content -Raw $path | ConvertFrom-Json

function Get-Node([string]$name) {
    $node = $wf.nodes | Where-Object { $_.name -eq $name } | Select-Object -First 1
    if (-not $node) { throw "Node not found: $name" }
    return $node
}

function Ensure-ConnectionNode([string]$from, [string]$to) {
    if (-not $wf.connections.PSObject.Properties[$from]) {
        $wf.connections | Add-Member -MemberType NoteProperty -Name $from -Value @{ main = @() }
    }
    $wf.connections.$from = @{ main = @(@([pscustomobject]@{ node = $to; type = 'main'; index = 0 })) }
}

function Add-SchemaFields($schema, [string[]]$fields) {
    foreach ($id in $fields) {
        if (-not ($schema | Where-Object { $_.id -eq $id })) {
            $schema += [pscustomobject]@{
                id = $id
                displayName = $id
                required = $false
                defaultMatch = $false
                display = $true
                type = 'string'
                canBeUsedToMatch = $true
                removed = $false
            }
        }
    }
    return $schema
}

$variation = Get-Node 'Variation Selector'
$variationCode = $variation.parameters.jsCode
if ($variationCode -notmatch 'hook_validation_batch_id') {
    $variationCode = $variationCode -replace "const store = \$getWorkflowStaticData\('global'\);", "const store = \$getWorkflowStaticData('global');`nstore.hook_validation_batch_id = store.hook_validation_batch_id || `new Date().toISOString().replace(/[:.]/g, '-');"
}
if ($variationCode -notmatch 'validation_batch_id:') {
    $variationCode = $variationCode -replace "validation_mode: 'hook_validation',", "validation_mode: 'hook_validation',`n      validation_batch_id: store.hook_validation_batch_id,"
}
$variation.parameters.jsCode = $variationCode

$buildLog = Get-Node 'Build Hook Validation Log'
$buildLog.parameters.jsCode = @'
const row = $input.all().map(i => i.json || {})[0] || {};
const recordType = String(row.record_type || 'validation_post').trim();
const batchId = String(row.validation_batch_id || '').trim();
const postId = String(row.content_id || row.content_key || '').trim();
if (recordType !== 'validation_post' || !postId || !batchId) return [];
return [{
  json: {
    record_type: 'validation_post',
    validation_batch_id: batchId,
    analysis_generated_at: '',
    post_id: postId,
    hook: String(row.hook_text || '').trim(),
    structure: String(row.structure_type || '').trim(),
    timestamp: String(row.timestamp || new Date().toISOString()).trim(),
    likes: String(row.likes || '0').trim(),
    saves: String(row.saves || '0').trim(),
    comments: String(row.comments || '0').trim(),
    dm_triggered: String(row.dm_triggered || 'false').trim()
  }
}];
'@

if (-not ($wf.nodes | Where-Object name -eq 'Hook Validation Analysis Webhook')) {
    $wf.nodes += [pscustomobject]@{
        id = [guid]::NewGuid().ToString()
        name = 'Hook Validation Analysis Webhook'
        type = 'n8n-nodes-base.webhook'
        typeVersion = 2
        position = @( -3248, 480 )
        parameters = @{
            httpMethod = 'POST'
            path = 'hook-validation-analysis'
            options = @{}
        }
        webhookId = [guid]::NewGuid().ToString()
    }
}

if (-not ($wf.nodes | Where-Object name -eq 'Read Hook Validation Log')) {
    $wf.nodes += [pscustomobject]@{
        id = [guid]::NewGuid().ToString()
        name = 'Read Hook Validation Log'
        type = 'n8n-nodes-base.googleSheets'
        typeVersion = 4
        position = @( -3008, 480 )
        credentials = @{ googleApi = @{ id = '0qLoNOqd9HAUAPaN'; name = 'Google Sheets account' } }
        parameters = @{
            authentication = 'serviceAccount'
            resource = 'sheet'
            operation = 'getRows'
            documentId = @{ __rl = $true; mode = 'id'; value = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q' }
            sheetName = @{ __rl = $true; mode = 'name'; value = 'improvement_log' }
            options = @{}
        }
    }
}

if (-not ($wf.nodes | Where-Object name -eq 'Build Hook Validation Analysis')) {
    $wf.nodes += [pscustomobject]@{
        id = [guid]::NewGuid().ToString()
        name = 'Build Hook Validation Analysis'
        type = 'n8n-nodes-base.code'
        typeVersion = 2
        position = @( -2768, 480 )
        parameters = @{
            mode = 'runOnceForAllItems'
            jsCode = @'
const rows = $input.all().map(i => i.json || {});
const isValidation = (r) => String(r.record_type || 'validation_post').trim() === 'validation_post';
const validationRows = rows.filter(isValidation);
if (!validationRows.length) return [];

const safeNum = (v) => {
  const n = Number(v || 0);
  return Number.isFinite(n) ? n : 0;
};
const safeBool = (v) => String(v || '').toLowerCase() === 'true' || String(v || '') === '1';
const safeTs = (v) => {
  const t = Date.parse(String(v || ''));
  return Number.isFinite(t) ? t : 0;
};
const now = new Date().toISOString();

const batchGroups = new Map();
for (const row of validationRows) {
  const key = String(row.validation_batch_id || '').trim() || '__legacy__';
  if (!batchGroups.has(key)) batchGroups.set(key, []);
  batchGroups.get(key).push(row);
}

const rankedBatches = [...batchGroups.entries()].map(([batchId, batchRows]) => {
  const latestTs = batchRows.reduce((m, r) => Math.max(m, safeTs(r.timestamp)), 0);
  return { batchId, batchRows, latestTs };
}).sort((a, b) => b.latestTs - a.latestTs || b.batchRows.length - a.batchRows.length);

const batch = rankedBatches[0];
const batchRows = batch.batchRows
  .slice()
  .sort((a, b) => safeTs(a.timestamp) - safeTs(b.timestamp) || safeNum(a.post_id) - safeNum(b.post_id))
  .slice(-15);

if (batchRows.length < 15) return [];

const scored = batchRows.map((r) => {
  const likes = safeNum(r.likes);
  const saves = safeNum(r.saves);
  const comments = safeNum(r.comments);
  const dmTriggered = safeBool(r.dm_triggered) ? 1 : 0;
  const score = likes * 1 + saves * 3 + comments * 4 + dmTriggered * 8;
  return { ...r, likes, saves, comments, dmTriggered, score };
});

const quartile = (arr, q) => {
  if (!arr.length) return 0;
  const sorted = arr.slice().sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const base = Math.floor(pos);
  const rest = pos - base;
  return sorted[base + 1] !== undefined ? sorted[base] + rest * (sorted[base + 1] - sorted[base]) : sorted[base];
};

const byHook = new Map();
const byStructure = new Map();
for (const r of scored) {
  const hook = String(r.hook || '').trim() || 'unknown_hook';
  const structure = String(r.structure || '').trim() || 'unknown_structure';
  if (!byHook.has(hook)) byHook.set(hook, []);
  if (!byStructure.has(structure)) byStructure.set(structure, []);
  byHook.get(hook).push(r);
  byStructure.get(structure).push(r);
}

function summarize(groups, keyName) {
  const out = [];
  for (const [key, rows] of groups.entries()) {
    const total_posts = rows.length;
    const total_score = rows.reduce((s, r) => s + r.score, 0);
    const avg_score = total_posts ? total_score / total_posts : 0;
    const dm_hits = rows.reduce((s, r) => s + (r.dmTriggered ? 1 : 0), 0);
    out.push({ [keyName]: key, total_posts, total_score, avg_score, dm_hits });
  }
  return out.sort((a, b) => b.avg_score - a.avg_score || b.dm_hits - a.dm_hits || b.total_score - a.total_score);
}

const hookSummary = summarize(byHook, 'hook');
const structureSummary = summarize(byStructure, 'structure');

const hookAvgScores = hookSummary.map(r => r.avg_score);
const structureAvgScores = structureSummary.map(r => r.avg_score);
const hookHi = quartile(hookAvgScores, 0.75);
const hookLo = quartile(hookAvgScores, 0.25);
const structHi = quartile(structureAvgScores, 0.75);
const structLo = quartile(structureAvgScores, 0.25);

const hookRows = hookSummary.map(r => ({
  record_type: 'hook_analysis',
  validation_batch_id: batch.batchId,
  analysis_generated_at: now,
  hook: r.hook,
  structure: '',
  total_posts: r.total_posts,
  total_score: r.total_score,
  avg_score: r.avg_score.toFixed(2),
  dm_hits: r.dm_hits,
  hook_status: (r.avg_score >= hookHi || r.dm_hits > 0) ? 'winner' : (r.avg_score <= hookLo && r.dm_hits === 0 ? 'loser' : 'neutral'),
  structure_status: '',
  hook_performance_summary: '',
  structure_performance_summary: '',
  recommended_hooks: '',
  suppressed_hooks: ''
}));

const structureRows = structureSummary.map(r => ({
  record_type: 'structure_analysis',
  validation_batch_id: batch.batchId,
  analysis_generated_at: now,
  hook: '',
  structure: r.structure,
  total_posts: r.total_posts,
  total_score: r.total_score,
  avg_score: r.avg_score.toFixed(2),
  dm_hits: r.dm_hits,
  hook_status: '',
  structure_status: (r.avg_score >= structHi || r.dm_hits > 0) ? 'winner' : (r.avg_score <= structLo && r.dm_hits === 0 ? 'loser' : 'neutral'),
  hook_performance_summary: '',
  structure_performance_summary: '',
  recommended_hooks: '',
  suppressed_hooks: ''
}));

const hookWinners = hookSummary.filter(r => r.avg_score >= hookHi || r.dm_hits > 0).map(r => r.hook);
const hookLosers = hookSummary.filter(r => r.avg_score <= hookLo && r.dm_hits === 0 && r.total_score <= quartile(hookSummary.map(r => r.total_score), 0.25)).map(r => r.hook);
const structureWinners = structureSummary.filter(r => r.avg_score >= structHi || r.dm_hits > 0).map(r => r.structure);
const structureLosers = structureSummary.filter(r => r.avg_score <= structLo && r.dm_hits === 0 && r.total_score <= quartile(structureSummary.map(r => r.total_score), 0.25)).map(r => r.structure);

const summaryRow = {
  record_type: 'winner_summary',
  validation_batch_id: batch.batchId,
  analysis_generated_at: now,
  hook: '',
  structure: '',
  total_posts: scored.length,
  total_score: scored.reduce((s, r) => s + r.score, 0),
  avg_score: scored.length ? (scored.reduce((s, r) => s + r.score, 0) / scored.length).toFixed(2) : '0.00',
  dm_hits: scored.reduce((s, r) => s + (r.dmTriggered ? 1 : 0), 0),
  hook_status: '',
  structure_status: '',
  hook_performance_summary: JSON.stringify(hookSummary),
  structure_performance_summary: JSON.stringify(structureSummary),
  recommended_hooks: hookWinners.join(' | '),
  suppressed_hooks: hookLosers.join(' | '),
  hook_winners: hookWinners.join(' | '),
  hook_losers: hookLosers.join(' | '),
  structure_winners: structureWinners.join(' | '),
  structure_losers: structureLosers.join(' | ')
};

return [
  ...hookRows.map(json => ({ json })),
  ...structureRows.map(json => ({ json })),
  { json: summaryRow }
];
'@
        }
    }
}

if (-not ($wf.nodes | Where-Object name -eq 'Append Hook Validation Analysis')) {
    $wf.nodes += [pscustomobject]@{
        id = [guid]::NewGuid().ToString()
        name = 'Append Hook Validation Analysis'
        type = 'n8n-nodes-base.googleSheets'
        typeVersion = 4
        position = @( -2528, 480 )
        continueOnFail = $true
        credentials = @{ googleApi = @{ id = '0qLoNOqd9HAUAPaN'; name = 'Google Sheets account' } }
        parameters = @{
            authentication = 'serviceAccount'
            resource = 'sheet'
            operation = 'append'
            documentId = @{ __rl = $true; mode = 'id'; value = '17pM1TO62U8wklrpmC5ZDPHNeNMNUT18hsOP9GJQ-d4Q' }
            sheetName = @{ __rl = $true; mode = 'name'; value = 'improvement_log' }
            columns = @{
                mappingMode = 'autoMapInputData'
                matchingColumns = @()
                attemptToConvertTypes = $false
                convertFieldsToString = $false
                schema = @()
                value = @{}
            }
            options = @{}
        }
    }
}

$schemaFields = @(
    'record_type','validation_batch_id','analysis_generated_at','post_id','hook','structure','timestamp','likes','saves','comments','dm_triggered',
    'total_posts','total_score','avg_score','dm_hits','hook_status','structure_status','hook_performance_summary','structure_performance_summary',
    'recommended_hooks','suppressed_hooks','hook_winners','hook_losers','structure_winners','structure_losers'
)

$seedImprovement = Get-Node 'Seed improvement_log headers'
$appendImprovement = Get-Node 'Append improvement_log headers'
$seedImprovement.parameters.columns.schema = Add-SchemaFields @($seedImprovement.parameters.columns.schema) $schemaFields
$appendImprovement.parameters.columns.schema = Add-SchemaFields @($appendImprovement.parameters.columns.schema) $schemaFields

$buildLog.parameters.jsCode = $buildLog.parameters.jsCode -replace "const recordType = String\(row\.record_type \|\| 'validation_post'\)\.trim\(\);", "const recordType = String(row.record_type || 'validation_post').trim();"

if (-not ($wf.connections.PSObject.Properties['Hook Validation Analysis Webhook'])) {
    $wf.connections | Add-Member -MemberType NoteProperty -Name 'Hook Validation Analysis Webhook' -Value @{ main = @() }
}
Ensure-ConnectionNode 'Hook Validation Analysis Webhook' 'Read Hook Validation Log'
Ensure-ConnectionNode 'Read Hook Validation Log' 'Build Hook Validation Analysis'
Ensure-ConnectionNode 'Build Hook Validation Analysis' 'Append Hook Validation Analysis'

$json = $wf | ConvertTo-Json -Depth 100
Set-Content -Path $path -Value $json -Encoding UTF8
