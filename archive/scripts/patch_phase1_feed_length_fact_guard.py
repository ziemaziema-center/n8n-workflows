import json
import re
import urllib.request

BASE = "http://43.201.227.194:5678"
API = re.search(r'API = "([^"]+)"', open("add_reel_pipeline_minimal.py", encoding="utf-8").read()).group(1)
WID = "KPa5tncCc87z2ZsE"


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

def node(name):
    return next(n for n in wf["nodes"] if n["name"] == name)

# Strengthen fact guard in Select Fact Items.
sel = node("Select Fact Items")
sel_js = sel["parameters"]["jsCode"]
sel_js = sel_js.replace(
    "if (!/\\d|4월|24일|10만원|37년/.test(fact)) fact = '최근 전자담배 규제 뉴스에서 ' + fact;",
    "if (!/\\d|4월|24일|10만원|37년/.test(fact)) fact = '4월 24일 시행 기준, ' + fact;"
)
sel["parameters"]["jsCode"] = sel_js

# Expand feed body to 200-250 Korean space-separated tokens.
bs = node("Build Simulation Content")
js = bs["parameters"]["jsCode"]
pattern = re.compile(r"const feedCaption = \(f\) => \{[\s\S]*?\n\};\n\nreturn slots\.map")
replacement = r'''const feedCaption = (f) => {
  const paragraphs = [
    `${f.fact} 이거 그냥 뉴스 제목 하나로 넘기면 손해다. 전자담배 규제는 이제 취향 문제가 아니라, 어디서 피우고, 어떻게 팔고, 어떤 문구를 붙일 수 있는지까지 한 번에 묶이는 문제로 바뀌고 있다. 예전처럼 “전담은 좀 다르지 않나” 하고 넘기면, 실제 현장에서는 금연구역, 과태료, 광고 문구, 매장 안내에서 바로 헷갈린다.`,
    `핵심은 합성니코틴 액상형 전자담배가 기존 담배 규제 바깥에 있던 시간이 끝났다는 거다. 보도와 정책자료 기준으로 4월 24일부터 담배 정의가 니코틴 제품까지 넓어지고, 건강경고 표시, 광고 제한, 금연구역 사용 금지 같은 규칙이 같이 따라온다. 그러니까 이건 단순히 제품 이름이 바뀐 문제가 아니다. 소비자가 어디서 써도 되는지, 매장이 어떻게 설명해야 하는지, 온라인 판매가 어디까지 가능한지까지 연결된다.`,
    `소비자 입장에서는 “작고 냄새 덜 나니까 괜찮겠지”라는 감각이 제일 위험하다. 규제가 바뀌면 단속은 감정이 아니라 기준으로 움직인다. 몰랐다는 말이 통할 수도 있지만, 돈은 보통 모르는 쪽에서 먼저 나간다. 특히 금연구역 과태료나 판매 제한 같은 건 나중에 검색해서 알면 늦다. 이미 계산대 앞이거나, 이미 피웠거나, 이미 잘못 안내받은 뒤일 수 있다.`,
    `더 웃긴 건 이 변화가 갑자기 도덕 문제처럼 포장된다는 점이다. 누군가는 청소년 보호라고 말하고, 누군가는 뒤늦게 만든 땜질 규제라고 말한다. 둘 다 어느 정도 맞을 수 있다. 그런데 정작 중요한 건 소비자가 정확한 기준을 제일 늦게 안다는 거다. 정책은 발표되고, 매장은 바뀌고, 가격표와 안내 문구는 움직이는데, 사용자는 그냥 평소처럼 들어간다.`,
    `그래서 지금 봐야 할 건 찬반보다 기준이다. 4월 24일 이후 합성니코틴 전담이 어떤 규제 안으로 들어갔는지, 금연구역과 광고 제한이 어떻게 붙는지, 매장에서 어떤 말이 달라지는지 확인해야 한다. 너라면 이걸 소비자 보호라고 보냐, 아니면 뒤늦게 만든 단속 장치라고 보냐?`
  ];
  return paragraphs.join("\n\n");
};

return slots.map'''
new_js, count = pattern.subn(replacement, js)
if count != 1:
    raise RuntimeError(f"feedCaption replacement failed count={count}")
bs["parameters"]["jsCode"] = new_js

body = {
    "name": wf["name"],
    "nodes": wf["nodes"],
    "connections": wf.get("connections", {}),
    "settings": wf.get("settings", {}),
    "staticData": wf.get("staticData", {}),
    "pinData": wf.get("pinData", {}),
}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print(json.dumps({"updated": ["Select Fact Items", "Build Simulation Content"], "feed_target_words": "200-250"}, ensure_ascii=False))
