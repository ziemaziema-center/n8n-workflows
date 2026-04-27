const first = $input.first();
const input = (first && first.json && typeof first.json === 'object') ? first.json : {};
const body = (input.body && typeof input.body === 'object') ? input.body : input;

const directAction = String(body.action || '').trim();
if (directAction === 'cache_reel') {
  const testId = String(body.test_id || '').trim();
  const videoUrl = String(body.video_url || body.reel_video_url || body.media_url || body.reel_url || '').trim();
  if (!testId || !/^https?:\/\//i.test(videoUrl)) {
    return [];
  }
  const store = $getWorkflowStaticData('global');
  store.reel_video_urls = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};
  store.reel_video_urls[testId] = videoUrl;
  store.reel_video_cached_at = new Date().toISOString();
  return [];
}

if (directAction === 'cache_carousel') {
  const testId = String(body.test_id || '').trim();
  const carousel = (body.carousel && typeof body.carousel === 'object') ? body.carousel : null;
  const media = Array.isArray(carousel?.media) ? carousel.media.filter((m) => String(m?.image_url || '').trim()) : [];
  if (!testId || media.length < 2) {
    return [];
  }

  // Preserve reel URL signal if provided in cache payload path.
  const bodyReelUrlCandidates = [
    body.video_url,
    body.reel_video_url,
    body.media_url,
    body.reel_url,
    body?.reel?.video_url,
    body?.carousel?.reel_video_url,
    body?.carousel?.video_url,
  ].map((v) => String(v || '').trim()).filter(Boolean);
  const cachedReelUrl = bodyReelUrlCandidates.find((u) => /^https?:\/\//i.test(u)) || '';

  const store = $getWorkflowStaticData('global');
  store.carousel_payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
  store.carousel_payloads[testId] = {
    caption: String(carousel.caption || '').trim(),
    media: media.map((m, idx) => ({ position: Number(m.position || (idx + 1)), image_url: String(m.image_url || '').trim() })),
    reel_video_url: cachedReelUrl,
    updated_at: new Date().toISOString(),
  };
  return [];
}

const callback = (body.callback_query && typeof body.callback_query === 'object') ? body.callback_query : null;
if (!callback) {
  return [];
}

const callbackData = String(callback.data || body.callback_data || '').trim();
const [actionRaw, testIdRaw] = callbackData.split('|');
const action = String(actionRaw || '').trim();
const testId = String(testIdRaw || '').trim();

const isReelApprove = action === 'approve_test' || action === 'approve' || action === 'approve_reel';
const isCarouselApprove = action === 'approve_carousel';
if (!isReelApprove && !isCarouselApprove) {
  return [];
}

if (!testId) {
  throw new Error('Missing test_id in approve callback');
}

const store = $getWorkflowStaticData('global');
store.clean_publish_guard = (store.clean_publish_guard && typeof store.clean_publish_guard === 'object') ? store.clean_publish_guard : {};
store.daily_publish_limit = Number(store.daily_publish_limit ?? 3);
store.daily_publish_success_log = Array.isArray(store.daily_publish_success_log) ? store.daily_publish_success_log : [];

const nowSeoul = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Seoul' }));
const todayKey = `${nowSeoul.getFullYear()}-${String(nowSeoul.getMonth() + 1).padStart(2, '0')}-${String(nowSeoul.getDate()).padStart(2, '0')}`;
store.daily_publish_success_log = store.daily_publish_success_log.slice(-300);
const todaySuccessCount = store.daily_publish_success_log.filter((r) => String(r.dateKey || '') === todayKey).length;
if (todaySuccessCount >= store.daily_publish_limit) {
  throw new Error(`DAILY_LIMIT_REACHED limit=${store.daily_publish_limit} count=${todaySuccessCount}`);
}

const dedupeKey = `${action}|${testId}`;
if (store.clean_publish_guard[dedupeKey]) {
  return [];
}
store.clean_publish_guard[dedupeKey] = new Date().toISOString();

const message = (callback.message && typeof callback.message === 'object') ? callback.message : ((body.message && typeof body.message === 'object') ? body.message : {});
const callbackCaption = String(message.caption || message.text || '');

if (isReelApprove) {
  const payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
  const payload = payloads[testId] && typeof payloads[testId] === 'object' ? payloads[testId] : null;

  const videoMap = (store.reel_video_urls && typeof store.reel_video_urls === 'object') ? store.reel_video_urls : {};
  const mappedVideoUrl = String(videoMap[testId] || '').trim();

  // Fallback order:
  // 1) staticData.global.reel_video_urls[test_id]
  // 2) callback/body payload fields
  // 3) cached carousel/static payload fields that may contain reel URL
  const callbackCandidates = [
    body.video_url,
    body.reel_video_url,
    body.media_url,
    body.reel_url,
    body?.reel?.video_url,
    body?.carousel?.reel_video_url,
    body?.carousel?.video_url,
  ].map((v) => String(v || '').trim()).filter(Boolean);

  const payloadCandidates = [
    payload?.reel_video_url,
    payload?.video_url,
    payload?.media_url,
    payload?.reel_url,
    payload?.reel?.video_url,
  ].map((v) => String(v || '').trim()).filter(Boolean);

  const callbackVideoUrl = callbackCandidates.find((u) => /^https?:\/\//i.test(u)) || '';
  const payloadVideoUrl = payloadCandidates.find((u) => /^https?:\/\//i.test(u)) || '';
  const finalVideoUrl = mappedVideoUrl || callbackVideoUrl || payloadVideoUrl;

  if (!finalVideoUrl) {
    throw new Error(`Reel asset missing for approved test_id ${testId}; publish blocked`);
  }

  if (/samplelib\.com|gtv-videos-bucket|ForBiggerJoyrides|ForBiggerEscapes/i.test(finalVideoUrl)) {
    throw new Error('Generic sample video blocked for approve flow');
  }

  return [{
    json: {
      route_action: 'approve_reel',
      callback_data: action,
      test_id: testId,
      caption: callbackCaption,
      video_url: finalVideoUrl,
      video_source: mappedVideoUrl ? 'reel_cache' : (callbackVideoUrl ? 'callback_payload' : 'carousel_payload'),
      approved_via: 'telegram_callback',
      arm_live_publish: true,
      daily_publish_limit: store.daily_publish_limit,
      daily_publish_count_today: todaySuccessCount,
    }
  }];
}

const payloads = (store.carousel_payloads && typeof store.carousel_payloads === 'object') ? store.carousel_payloads : {};
const payload = payloads[testId] && typeof payloads[testId] === 'object' ? payloads[testId] : null;
const media = Array.isArray(payload?.media) ? payload.media : [];
if (!payload || media.length < 2) {
  throw new Error(`Carousel media payload missing for approved test_id ${testId}`);
}

return [{
  json: {
    route_action: 'approve_carousel',
    callback_data: action,
    test_id: testId,
    caption: String(payload.caption || callbackCaption || '').trim(),
    carousel: {
      caption: String(payload.caption || callbackCaption || '').trim(),
      media,
    },
    approved_via: 'telegram_callback',
    arm_live_publish: true,
    daily_publish_limit: store.daily_publish_limit,
    daily_publish_count_today: todaySuccessCount,
  }
}];
