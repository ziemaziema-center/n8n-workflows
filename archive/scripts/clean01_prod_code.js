const store = $getWorkflowStaticData('global');
if (typeof store.mediaIndex !== 'number') store.mediaIndex = 0;

const id = String(Date.now()) + '-' + Math.random().toString(36).slice(2, 8);
const medias = [
  'https://samplelib.com/lib/preview/mp4/sample-5s.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
  'https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
];
const media = medias[store.mediaIndex % medias.length];
store.mediaIndex = (store.mediaIndex + 1) % medias.length;

const seeds = [
  {
    topic: 'price_policy',
    hook: '담배값 1만원 가면, 전자담배 매장부터 갈린다',
    l1: '가격 인상 이슈가 뜨면 구매 동선이 먼저 바뀜.',
    l2: '문제는 제품보다 회전 속도와 객단가 분리.',
    l3: '이 구간 놓치면 재고랑 마진이 같이 흔들림.',
    end: '여기서 대부분 대응 순서부터 틀린다.',
    tags: ['#전자담배', '#베이프', '#정책이슈', '#매장운영', '#시장변화'],
  },
  {
    topic: 'regulation',
    hook: '단속 기준 바뀌면, 매출보다 먼저 터지는 게 있다',
    l1: '표시는 같아 보여도 적용 기준은 이미 달라짐.',
    l2: '응대 문구 하나가 민원과 리뷰를 갈라버림.',
    l3: '버티면 누적 리스크가 비용으로 바뀜.',
    end: '이 기준은 공개 글에서 끝까지 못 푼다.',
    tags: ['#전자담배', '#베이프매장', '#규정체크', '#운영리스크', '#매출방어'],
  },
  {
    topic: 'market_shift',
    hook: '요즘 베이프 잘 나가는 매장, 공통점 하나 있음',
    l1: '신제품보다 회전 구조를 먼저 바꿈.',
    l2: '고객은 맛보다 선택 피로에서 먼저 이탈함.',
    l3: '진열과 권장 순서에서 매출이 갈림.',
    end: '이 포인트 놓치면 계속 할인으로 버티게 된다.',
    tags: ['#전자담배', '#베이프샵', '#고객심리', '#재고회전', '#마진구조'],
  },
];

const pick = seeds[Number(String(Date.now()).slice(-2)) % seeds.length];
const caption = [pick.hook, pick.l1, pick.l2, pick.l3, pick.end, pick.tags.join(' ')].join('\n');

const item = {
  simulation_mode: false,
  mode: 'production_content',
  niche: 'vape',
  content_type: 'vape_news_info',
  test_id: id,
  topic: pick.topic,
  hook: pick.hook,
  body_lines: [pick.l1, pick.l2, pick.l3],
  tension_ending: pick.end,
  hashtags: pick.tags.join(' '),
  caption,
  video_url: media,
  chat_id: '7592247598',
  dm_response_library: {
    general_user: [
      '지금 보신 건 공개 가능한 범위만 정리한 겁니다.',
      '정보만 보면 계속 같은 구간에서 막힙니다.',
    ],
    curious_user: [
      '핵심은 제품보다 운영 기준 순서입니다.',
      '이 다음 단계는 공개형으로 다 못 풉니다.',
    ],
    business_owner: [
      '이건 그냥 정보가 아니라 운영 구조 이슈입니다.',
      '마진, 회전, 리스크를 같이 봐야 결론이 맞습니다.',
    ],
    skeptical_user: ['의심은 맞는 반응입니다.', '결과보다 기준부터 맞춰야 판단이 됩니다.'],
    extractor_user: ['공개 DM에서는 여기까지만 공유합니다.', '핵심 구조는 단계 확인 전에는 열지 않습니다.'],
    follow_up_question: ['지금 개인용 기준인가요, 매장 운영 기준인가요?'],
  },
  dm_routing_hints: {
    business_owner_keywords: ['매장', '운영', '재고', '마진', '회전', '발주', '진열', '리스크'],
    low_value_patterns: ['그냥 정보', '요약만', '정답만'],
    boundary_rule: 'never_fully_reveal_core',
  },
  reply_markup: JSON.stringify({
    inline_keyboard: [
      [{ text: 'Approve', callback_data: 'approve_test|' + id }],
      [{ text: 'Regen Text', callback_data: 'regen_text|' + id }],
      [{ text: 'Regen Media', callback_data: 'regen_media|' + id }],
      [{ text: 'Delete', callback_data: 'delete_test|' + id }],
    ],
  }),
};

return [{ json: item }];
