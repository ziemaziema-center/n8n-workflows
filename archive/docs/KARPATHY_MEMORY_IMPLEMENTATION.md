# Simplified Karpathy Memory Changes

Last updated: 2026-04-16

## Storage

Use only two sheets in `content_db`:

- `memory_current_rules`
- `memory_log`

### `memory_current_rules` columns

- `rule_priority`
- `rule_text`
- `updated_at`

### `memory_log` columns

- `hook`
- `performance_score`
- `result`
- `reason`
- `logged_at`

## Updated Simplified Node Changes Only

### 1. `01_Content_Generator_live`

Keep this as the only workflow that loads memory before generation.

#### Change existing node

- `OpenAI Generate Draft`

#### Add only these nodes

1. `Read Current Rules`
- Type: `Google Sheets`
- Place before `OpenAI Generate Draft`
- Read from `memory_current_rules`

2. `Build Current Rules Prompt`
- Type: `Code`
- Place after `Read Current Rules`

3. `Merge Memory With Articles`
- Type: `Merge`
- Place before `OpenAI Generate Draft`
- Input 1: article items from `Deduplicate + Filter`
- Input 2: compiled rules from `Build Current Rules Prompt`

#### `Build Current Rules Prompt` code

```javascript
const rows = items
  .map(i => i.json)
  .sort((a, b) => Number(a.rule_priority || 999) - Number(b.rule_priority || 999))
  .slice(0, 10);

const current_rules_prompt = rows.length
  ? [
      '[COMPILED CURRENT RULES - 반드시 우선 반영]',
      ...rows.map(r => `- ${r.rule_text}`)
    ].join('\n')
  : '[COMPILED CURRENT RULES - 반드시 우선 반영]\n- No current rules yet. Use strong hook, clear message, and save/share trigger.';

return [{ json: { current_rules_prompt } }];
```

#### Exact prompt change in `OpenAI Generate Draft`

Inject only this variable at the TOP of the user prompt, before the article input:

```text
{{$json.current_rules_prompt}}

규칙:
- 위 current_rules를 기사 해석보다 먼저 적용하라.
- 규칙은 짧고 강한 후킹, 저장 유도, 명확성을 우선한다.
```

Nothing else in the generation flow needs to change.

### 2. `05_Performance_Analyzer`

Simplify this workflow into one logging step for memory.

#### Change existing node

- `OpenAI Analyze Performance`

#### Change existing node

- `Parse Performance JSON`

#### Remove need for extra pattern outputs

Do not create:

- `winning_patterns`
- `failure_patterns`
- `hook_patterns`

Log only:

- `hook`
- `performance_score`
- `result`
- `reason`

#### Exact prompt change in `OpenAI Analyze Performance`

Replace the current prompt with:

```text
다음 게시물 성과를 분석해서 memory_log용 JSON만 반환하라.

입력 데이터:
{{$json}}

판단 규칙:
- performance_score가 높고 성과가 좋으면 result는 good
- 성과가 약하면 result는 bad
- hook은 게시물의 핵심 첫 문장 또는 썸네일 훅을 짧게 정리
- reason은 짧은 구문만 쓴다
- 예시: strong curiosity, weak clarity, weak stop-scroll, good save trigger

반드시 JSON만:
{
  "hook": "",
  "performance_score": 0,
  "result": "good|bad",
  "reason": ""
}
```

#### Exact change in `Parse Performance JSON`

Normalize only the minimal fields:

```javascript
const txt = $json.choices?.[0]?.message?.content || '{}';
let parsed = {};
let parseFailed = false;
try {
  parsed = JSON.parse(txt);
} catch (e) {
  parseFailed = true;
  parsed = {};
}

const base = $item(0).$node["Get Media Insights"].json || {};

return [{
  json: {
    hook: parsed.hook || base.thumbnail_hook || base.final_title || '',
    performance_score: Number(parsed.performance_score || 0),
    result: parseFailed ? 'bad' : (parsed.result || 'bad'),
    reason: parseFailed
      ? 'parse failed'
      : String(parsed.reason || '').trim().slice(0, 60),
    logged_at: new Date().toISOString()
  }
}];
```

#### Repoint existing append node

- Change `Append Self Improving`
- Target sheet: `memory_log`

Keep `Append Progress Update` only if you still want audit/history.

### 3. `05_Auto_Improvement`

Simplify to one compression pass from recent `memory_log`.

#### Replace workflow purpose

- Read recent `memory_log`
- Compress into 5-10 rules
- Overwrite `memory_current_rules`

#### Change existing node

- `Read 7 Day Metrics`

Change it to:

- Read `memory_log`

#### Replace existing code node

- Replace `Rank Top Performers`

With a minimal recent-log selector:

```javascript
const rows = items
  .map(i => i.json)
  .sort((a, b) => new Date(a.logged_at || 0).getTime() - new Date(b.logged_at || 0).getTime())
  .slice(-50);
return [{ json: { memory_log: rows } }];
```

#### Replace existing GPT node purpose

- Replace `GPT Generate Hook Templates`

With:

- `OpenAI Compress Current Rules`

#### Exact prompt for `OpenAI Compress Current Rules`

```text
아래 recent memory_log를 current_rules로 압축하라.

원칙:
- 5~10개 규칙만 남긴다
- good 결과에서 반복되는 패턴은 강화한다
- bad 결과에서 반복되는 패턴은 금지 규칙으로 바꾼다
- 문장은 짧고 명령형으로 쓴다

memory_log:
{{$json.memory_log}}

반드시 JSON만:
{
  "current_rules": [
    {"rule_priority": 1, "rule_text": ""},
    {"rule_priority": 2, "rule_text": ""},
    {"rule_priority": 3, "rule_text": ""}
  ]
}
```

#### Replace parsing node

- Replace `Parse Hook Templates`

With:

```javascript
const content = $json.choices?.[0]?.message?.content || '{}';
let parsed = {};
try { parsed = JSON.parse(content); } catch (e) { parsed = {}; }

const now = new Date().toISOString();
const rules = Array.isArray(parsed.current_rules) ? parsed.current_rules.slice(0, 10) : [];

return rules.map((rule, idx) => ({
  json: {
    rule_priority: Number(rule.rule_priority || idx + 1),
    rule_text: String(rule.rule_text || '').trim(),
    updated_at: now
  }
})).filter(item => item.json.rule_text);
```

#### Replace final write node

- Replace `Update Templates Sheet`
- Target sheet: `memory_current_rules`

Implementation note:

- Fully replace the `memory_current_rules` sheet contents each cycle.
- Do not append on top of old `current_rules`.
- Write only the newest `5-10` active rules.
- Exact method:
- Add a `Clear Current Rules Sheet` step first
- Then append the freshly parsed `5-10` rules only
- Do not add extra merge/corpus logic.

### 4. `04_Performance_Tracking`

No major redesign needed.

Only keep enough source data so `05_Performance_Analyzer` can infer a hook:

- `thumbnail_hook` if available
- otherwise `final_title`

If that data is already available in downstream rows, do not add anything else.

## Stable Minimal Flow

1. `01_Content_Generator_live`
- read `memory_current_rules`
- inject rules at top of prompt

2. `05_Performance_Analyzer`
- analyze result into one minimal `memory_log` row

3. `05_Auto_Improvement`
- read recent `memory_log`
- compress into `memory_current_rules`

No extra pattern sheets.
No complex metadata.
No workflow rebuild.
