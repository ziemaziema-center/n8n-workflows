const fs = require('fs');

const workflowPath = process.argv[2] || 'workflows/live/clean_01_generator.json';
const raw = JSON.parse(fs.readFileSync(workflowPath, 'utf8'));
const workflow = Array.isArray(raw) ? raw[0] : raw;

const nodeName = 'Convert Carousel PNG to JPEG';
if (workflow.nodes.some((node) => node.name === nodeName)) {
  console.log('node already exists');
  process.exit(0);
}

const buildNode = workflow.nodes.find((node) => node.name === 'Build Carousel Media Array');
const nextNode = workflow.nodes.find((node) => node.name === 'Prepare Carousel Approval Cache');
if (!buildNode || !nextNode) {
  throw new Error('Required carousel nodes not found');
}

const jsCode = `const items = $input.all();
const out = [];

function sanitize(value) {
  return String(value || '').replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 80) || 'carousel';
}

for (const item of items) {
  const j = { ...(item.json || {}) };
  const originalUrl = String(j.image_url || '').trim();
  if (!originalUrl) {
    out.push(item);
    continue;
  }

  if (/\\.jpe?g(\\?|$)/i.test(originalUrl)) {
    out.push(item);
    continue;
  }

  const testId = sanitize(j.test_id || 'carousel');
  const position = String(j.position || j.carousel_slide_index || 1).padStart(2, '0');
  const rand = Math.random().toString(36).slice(2, 10);
  const filename = \`carousel_\${testId}_\${position}_\${rand}.jpg\`;

  const saveRes = await this.helpers.httpRequest({
    method: 'POST',
    url: 'http://43.201.227.194:8000/save-image',
    body: { image_url: originalUrl, filename },
    json: true,
    timeout: 60000,
  });

  const jpgUrl = String((saveRes && saveRes.permanent_url) || '').trim();
  if (!/^https?:\\/\\//i.test(jpgUrl) || !/\\.jpe?g(\\?|$)/i.test(jpgUrl)) {
    throw new Error(\`JPEG conversion failed for carousel image \${originalUrl}\`);
  }

  const carousel = (j.carousel && typeof j.carousel === 'object') ? { ...j.carousel } : {};
  const media = Array.isArray(carousel.media)
    ? carousel.media.map((m) => ({
        ...m,
        image_url: Number(m.position || 0) === Number(j.position || 0) ? jpgUrl : String(m.image_url || jpgUrl),
      }))
    : carousel.media;

  out.push({
    json: {
      ...j,
      image_url: jpgUrl,
      carousel_original_image_url: originalUrl,
      carousel_jpeg_converted: true,
      carousel: { ...carousel, media },
    },
    pairedItem: item.pairedItem,
  });
}

return out;`;

const newNode = {
  parameters: {
    mode: 'runOnceForAllItems',
    jsCode,
  },
  id: 'clean-gen-carousel-jpeg-convert',
  name: nodeName,
  type: 'n8n-nodes-base.code',
  typeVersion: 2,
  position: [
    Math.round((buildNode.position[0] + nextNode.position[0]) / 2),
    Math.round((buildNode.position[1] + nextNode.position[1]) / 2),
  ],
};

workflow.nodes.push(newNode);

const buildConn = workflow.connections['Build Carousel Media Array'];
if (!buildConn?.main?.[0]) {
  throw new Error('Build Carousel Media Array connection not found');
}
buildConn.main[0] = buildConn.main[0].map((conn) =>
  conn.node === 'Prepare Carousel Approval Cache'
    ? { node: nodeName, type: 'main', index: 0 }
    : conn
);
workflow.connections[nodeName] = {
  main: [[{ node: 'Prepare Carousel Approval Cache', type: 'main', index: 0 }]],
};

fs.writeFileSync(workflowPath, JSON.stringify(raw, null, 2) + '\n');
console.log('added ' + nodeName);
