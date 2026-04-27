# Carousel Payload Fix — 2026-04-26

## Root Cause
`Cache Carousel Approval Payload` in clean_01 sends `cache_carousel` to clean_02 webhook
with `continueOnFail: true` → failures swallowed silently → clean_02's `carousel_payloads[testId]`
is never written → `queue_carousel` click throws `Queue carousel blocked: missing carousel media`.

## Fix Overview
- **clean_01**: Store carousel payload in clean_01's OWN staticData + expose a fetch webhook
- **clean_02**: When local cache miss → fetch from clean_01 webhook as fallback

---

## STEP 1: Edit `Prepare Carousel Approval Cache` in clean_01_generator

Open n8n → clean_01_generator → find Code node "Prepare Carousel Approval Cache"
Replace the entire jsCode with:

```javascript
const all = $input.all().map(i => i.json || {});
const groups = new Map();
for (const item of all) {
  const id = String(item.test_id || '').trim();
  const image = String(item.image_url || '').trim();
  if (!id || !image) continue;
  if (!groups.has(id)) groups.set(id, []);
  groups.get(id).push(item);
}

// Store in clean_01's OWN staticData as reliable local backup
const store = $getWorkflowStaticData('global');
store.carousel_payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};

const out = [];
for (const [testId, items] of groups.entries()) {
  items.sort((a,b) => Number(a.position || 0) - Number(b.position || 0));
  const first = items[0] || {};
  const carousel = first.carousel && typeof first.carousel === 'object' ? first.carousel : {};
  const media = items.map((m, idx) => ({ position: Number(m.position || idx + 1), image_url: String(m.image_url || '').trim() })).filter(m => m.image_url);
  if (media.length < 2) continue;

  store.carousel_payloads[testId] = {
    caption: String(carousel.caption || first.caption || '').trim(),
    media,
    updated_at: new Date().toISOString(),
  };

  out.push({
    json: {
      ...first,
      action: 'cache_carousel',
      test_id: testId,
      carousel: { ...carousel, media },
      carousel_media_count: media.length
    }
  });
}
return out;
```

---

## STEP 2: Add "Carousel Fetch Webhook" to clean_01_generator

In n8n UI, open clean_01_generator and add TWO new nodes:

### Node A: Webhook trigger
- Type: `Webhook`
- Name: `Carousel Fetch Webhook`
- HTTP Method: GET
- Path: `clean_01_get_carousel`
- Respond: `Using 'Respond to Webhook' Node` (or `Last Node`)

### Node B: Code node
- Type: `Code`
- Name: `Return Carousel Payload`
- Mode: Run Once for All Items
- jsCode:

```javascript
const first = $input.first();
const query = first.json.query && typeof first.json.query === 'object' ? first.json.query : {};
const testId = String(query.test_id || first.json.test_id || '').trim();
if (!testId) {
  return [{ json: { found: false, error: 'missing test_id' } }];
}
const store = $getWorkflowStaticData('global');
const payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
const payload = (payloads[testId] && typeof payloads[testId] === 'object') ? payloads[testId] : null;
if (!payload || !Array.isArray(payload.media) || payload.media.length < 2) {
  return [{ json: { found: false, test_id: testId } }];
}
return [{ json: { found: true, test_id: testId, caption: payload.caption, media: payload.media } }];
```

### Connection:
`Carousel Fetch Webhook` → `Return Carousel Payload`

---

## STEP 3: Edit `Normalize Callback` in clean_02_approval

Open n8n → clean_02_approval → find Code node "Normalize Callback"
Locate the queue_carousel validation block (around line: `if (typeFromAction === 'carousel') {`)
Replace ONLY that block:

**BEFORE:**
```javascript
  if (typeFromAction === 'carousel') {
    const media = Array.isArray(carouselPayload?.media) ? carouselPayload.media : [];
    if (media.length < 2) {
      throw new Error(`Queue carousel blocked: missing carousel media for ${testId}`);
    }
  }
```

**AFTER:**
```javascript
  if (typeFromAction === 'carousel') {
    if (!carouselPayload || !Array.isArray(carouselPayload.media) || carouselPayload.media.length < 2) {
      // Fallback: fetch from clean_01's local cache
      try {
        const fetchRes = await this.helpers.httpRequest({
          method: 'GET',
          url: `http://localhost:5678/webhook/clean_01_get_carousel?test_id=${encodeURIComponent(testId)}`,
          returnFullResponse: false,
          timeout: 6000,
        });
        const parsed = typeof fetchRes === 'string' ? JSON.parse(fetchRes) : fetchRes;
        if (parsed && parsed.found && Array.isArray(parsed.media) && parsed.media.length >= 2) {
          carouselPayload = { caption: String(parsed.caption || '').trim(), media: parsed.media };
          store.carousel_payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
          store.carousel_payloads[testId] = { ...carouselPayload, updated_at: new Date().toISOString() };
        }
      } catch (e) { /* fetch failed, fall through */ }
    }
    const media = Array.isArray(carouselPayload?.media) ? carouselPayload.media : [];
    if (media.length < 2) {
      throw new Error(`Queue carousel blocked: missing carousel media for ${testId} (cache miss + fetch fallback failed)`);
    }
  }
```

---

## STEP 4: Verify `Cache Carousel Approval Payload` (clean_01) — optional hardening

Find the HTTP Request node "Cache Carousel Approval Payload" in clean_01_generator.
Change `continueOnFail` from `true` to `false`.
This ensures: if clean_02 webhook is unreachable, the entire carousel branch fails visibly
and the Telegram preview is NOT sent (preventing an unactionable preview).

> ⚠️ Only do Step 4 after confirming Steps 1-3 work. If you keep continueOnFail=true,
> the fallback in Step 3 handles the miss. If you set it to false, failures are visible
> but Telegram preview won't send if the POST fails.

---

## Test Sequence (after applying)

1. Manually trigger clean_01_generator (or wait for cron)
2. Receive Telegram carousel preview → click "Queue CAROUSEL X"
3. Expected: no error — queue success message (or silent success since queue returns [])
4. Verify in clean_02 staticData: `carousel_payloads` has new testId entry
5. Verify Phase 3C scheduler picks it up at scheduled time

---

## Rollback
Most recent backups:
- `clean_02_approval_backup_error_workflow_link_20260425_235020.json`
- `clean_01_generator_backup_strict_angle_rotation_20260426_004624.json`
