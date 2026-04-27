// Carousel payload fix patcher — run with: node apply_carousel_patch.js
const fs = require('fs');
const path = require('path');

const BASE = path.dirname(__filename);
const NOW = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);

// ── Patch clean_01_generator ──────────────────────────────────────────────────

const CLEAN01_SRC = path.join(BASE, 'clean_01_generator_backup_strict_angle_rotation_20260426_004624.json');
const CLEAN01_DST = path.join(BASE, `clean_01_generator_backup_carousel_payload_fix_${NOW}.json`);

const PREPARE_CAROUSEL_CODE = `const all = $input.all().map(i => i.json || {});
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
return out;`;

const FETCH_WEBHOOK_NODE = {
  id: 'carousel-fetch-webhook-node',
  name: 'Carousel Fetch Webhook',
  type: 'n8n-nodes-base.webhook',
  typeVersion: 2,
  position: [1720, -420],
  parameters: {
    path: 'clean_01_get_carousel',
    httpMethod: 'GET',
    responseMode: 'lastNode',
    options: {},
  },
  webhookId: 'carousel-fetch-' + Math.random().toString(36).slice(2, 10),
};

const RETURN_CAROUSEL_NODE = {
  id: 'return-carousel-payload-node',
  name: 'Return Carousel Payload',
  type: 'n8n-nodes-base.code',
  typeVersion: 2,
  position: [1960, -420],
  parameters: {
    mode: 'runOnceForAllItems',
    jsCode: `const first = $input.first();
const raw = first.json || {};
const query = raw.query && typeof raw.query === 'object' ? raw.query : {};
const testId = String(query.test_id || raw.test_id || '').trim();
if (!testId) {
  return [{ json: { found: false, error: 'missing test_id' } }];
}
const store = $getWorkflowStaticData('global');
const payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
const payload = (payloads[testId] && typeof payloads[testId] === 'object') ? payloads[testId] : null;
if (!payload || !Array.isArray(payload.media) || payload.media.length < 2) {
  return [{ json: { found: false, test_id: testId } }];
}
return [{ json: { found: true, test_id: testId, caption: payload.caption, media: payload.media } }];`,
  },
};

function patchClean01() {
  const wf = JSON.parse(fs.readFileSync(CLEAN01_SRC, 'utf8'));

  // 1. Patch Prepare Carousel Approval Cache
  const prepNode = wf.nodes.find(n => n.id === 'prepare-carousel-approval-cache-node');
  if (!prepNode) { console.error('ERROR: prepare-carousel-approval-cache-node not found in clean_01'); process.exit(1); }
  prepNode.parameters.jsCode = PREPARE_CAROUSEL_CODE;
  console.log('✓ Patched Prepare Carousel Approval Cache');

  // 2. Add new fetch webhook + code nodes
  const alreadyHasFetch = wf.nodes.some(n => n.id === 'carousel-fetch-webhook-node');
  if (!alreadyHasFetch) {
    wf.nodes.push(FETCH_WEBHOOK_NODE);
    wf.nodes.push(RETURN_CAROUSEL_NODE);
    console.log('✓ Added Carousel Fetch Webhook + Return Carousel Payload nodes');
  } else {
    console.log('  (fetch nodes already present, skipping add)');
  }

  // 3. Add connections for the new nodes (if not already there)
  wf.connections = wf.connections || {};
  if (!wf.connections['Carousel Fetch Webhook']) {
    wf.connections['Carousel Fetch Webhook'] = {
      main: [[{ node: 'Return Carousel Payload', type: 'main', index: 0 }]],
    };
    console.log('✓ Added connection: Carousel Fetch Webhook → Return Carousel Payload');
  }

  // 4. Update metadata
  wf.updatedAt = new Date().toISOString();

  fs.writeFileSync(CLEAN01_DST, JSON.stringify(wf, null, 2), 'utf8');
  console.log('✓ Written:', path.basename(CLEAN01_DST));
}

// ── Patch clean_02_approval ───────────────────────────────────────────────────

const CLEAN02_SRC = path.join(BASE, 'clean_02_approval_backup_error_workflow_link_20260425_235020.json');
const CLEAN02_DST = path.join(BASE, `clean_02_approval_backup_carousel_payload_fix_${NOW}.json`);

// The new queue_carousel validation block with fallback fetch
const CAROUSEL_VALIDATION_BEFORE = `  if (typeFromAction === 'carousel') {
    const media = Array.isArray(carouselPayload?.media) ? carouselPayload.media : [];
    if (media.length < 2) {
      throw new Error(\`Queue carousel blocked: missing carousel media for \${testId}\`);
    }
  }`;

const CAROUSEL_VALIDATION_AFTER = `  if (typeFromAction === 'carousel') {
    if (!carouselPayload || !Array.isArray(carouselPayload.media) || carouselPayload.media.length < 2) {
      try {
        const fetchRes = await this.helpers.httpRequest({
          method: 'GET',
          url: \`http://localhost:5678/webhook/clean_01_get_carousel?test_id=\${encodeURIComponent(testId)}\`,
          returnFullResponse: false,
          timeout: 6000,
        });
        const parsed = typeof fetchRes === 'string' ? JSON.parse(fetchRes) : fetchRes;
        if (parsed && parsed.found && Array.isArray(parsed.media) && parsed.media.length >= 2) {
          carouselPayload = { caption: String(parsed.caption || '').trim(), media: parsed.media };
          store.carousel_payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
          store.carousel_payloads[testId] = { ...carouselPayload, updated_at: new Date().toISOString() };
        }
      } catch (e) { /* fetch failed, fall through to error */ }
    }
    const media = Array.isArray(carouselPayload?.media) ? carouselPayload.media : [];
    if (media.length < 2) {
      throw new Error(\`Queue carousel blocked: missing carousel media for \${testId} (cache miss + fetch fallback failed)\`);
    }
  }`;

function patchClean02() {
  const wf = JSON.parse(fs.readFileSync(CLEAN02_SRC, 'utf8'));

  const normNode = wf.nodes.find(n => n.name === 'Normalize Callback');
  if (!normNode) { console.error('ERROR: Normalize Callback not found in clean_02'); process.exit(1); }

  const oldCode = normNode.parameters.jsCode;
  if (!oldCode.includes("Queue carousel blocked: missing carousel media")) {
    console.error('ERROR: Expected queue_carousel error string not found — code may have changed');
    process.exit(1);
  }

  // Patch: replace the validation block
  const newCode = oldCode.replace(
    /if \(typeFromAction === 'carousel'\) \{\s+const media = Array\.isArray\(carouselPayload\?\.media\) \? carouselPayload\.media : \[\];\s+if \(media\.length < 2\) \{\s+throw new Error\(`Queue carousel blocked: missing carousel media for \$\{testId\}`\);\s+\}\s+\}/,
    CAROUSEL_VALIDATION_AFTER
  );

  if (newCode === oldCode) {
    console.error('ERROR: Regex did not match — could not patch Normalize Callback. Apply manually from patch_carousel_payload_fix_20260426.md');
    // Still write the file with a note
    normNode.parameters._patchNote = 'MANUAL PATCH REQUIRED: see patch_carousel_payload_fix_20260426.md STEP 3';
  } else {
    normNode.parameters.jsCode = newCode;
    console.log('✓ Patched Normalize Callback (queue_carousel fallback fetch)');
  }

  wf.updatedAt = new Date().toISOString();
  fs.writeFileSync(CLEAN02_DST, JSON.stringify(wf, null, 2), 'utf8');
  console.log('✓ Written:', path.basename(CLEAN02_DST));
}

// ── Run ───────────────────────────────────────────────────────────────────────

console.log('\n=== Applying carousel payload fix ===\n');
console.log('--- clean_01_generator ---');
patchClean01();
console.log('\n--- clean_02_approval ---');
patchClean02();
console.log('\nDone. Import the patched JSON files into n8n to apply.');
console.log('See patch_carousel_payload_fix_20260426.md for manual steps if needed.');
