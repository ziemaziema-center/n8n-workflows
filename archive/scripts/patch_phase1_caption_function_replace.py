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
n = next(x for x in wf["nodes"] if x["name"] == "Build Simulation Content")
js = n["parameters"]["jsCode"]
start = js.index("const reelCaption =")
end = js.index("const feedCaption =", start)
new_block = r'''const reelCaption = (f) => [
  f.fact,
  f.jab,
  `팩트만 보면 더 불편하다. 4월 24일 이후 합성니코틴 전담은 더 이상 애매한 회색지대가 아니다. 금연구역, 광고 제한, 건강경고, 판매 방식까지 한 번에 묶이면 제일 늦게 맞는 건 늘 소비자다. 매장은 바뀐 룰을 알고 움직이는데, 손님은 예전 감각으로 들어간다. 그 차이에서 돈이 새고, 과태료가 생기고, 이상한 추천도 먹힌다.`,
  `여기서 웃긴 건 다들 “보호”라는 말만 반복한다는 거다. 보호라면 왜 사람들은 매장 앞에서야 알까. 보호라면 왜 가격표와 안내문은 바뀌는데 설명은 항상 늦을까. 이 채널에서 보는 건 제품 자랑이 아니라 그 뒤의 구조다. 겉으로는 건강 명분, 뒤로는 비용과 선택권의 재배치다.`,
  `이걸 모르면 다음에 매장 가서도 똑같이 당한다. 표면에는 건강, 안전, 보호 같은 단어가 붙는다. 그런데 실제로는 가격표, 사용 가능 장소, 판매 문구, 추천 순서가 조용히 바뀐다. 사람들은 제품을 고른다고 생각하지만 사실 바뀐 규칙 안에서 남은 선택지를 고르는 거다. 이 차이를 아는 사람은 질문을 다르게 하고, 모르는 사람은 그냥 계산한다. 이거 그냥 규제 강화라고 넘길 거야, 아니면 네 지갑이랑 선택권이 어디서 털리는지 볼 거야?`
].join("\n");
const carouselCaption = (f) => [
  f.fact,
  f.jab,
  `겉으로는 규제 정리처럼 보인다. 그런데 이면을 보면 소비자가 제일 늦게 배우는 게임이다. 매장은 안내문을 바꾸고, 판매 가능 문구를 조절하고, 추천 순서를 바꾼다. 손님은 그냥 평소처럼 들어가서 “왜 갑자기 이게 안 돼?”를 묻는다. 이 차이가 돈이 된다.`,
  `진짜 봐야 할 건 제품이 아니라 기준이다. 금연구역, 과태료, 광고 제한, 건강경고가 한 번에 붙으면 선택은 좁아지고 설명은 어려워진다. 겉으로는 안전한 제도처럼 보이지만, 뒤에서는 누가 먼저 알고 누가 늦게 아는지가 갈린다. 먼저 아는 쪽은 안내문을 바꾸고, 늦게 아는 쪽은 계산대 앞에서 당황한다. 누군가는 보호라고 말하겠지만, 누군가는 이걸 늦게 온 단속이라고 부를 거다.`,
  f.question
].join("\n");
'''
n["parameters"]["jsCode"] = js[:start] + new_block + js[end:]
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf.get("connections", {}), "settings": wf.get("settings", {}), "staticData": wf.get("staticData", {}), "pinData": wf.get("pinData", {})}
req(f"/api/v1/workflows/{WID}", "PUT", body)
print("caption functions replaced")
