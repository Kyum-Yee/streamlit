"""선지를 3차원 벡터로 놓고 코사인 유사도·난도 지수를 계산한다.

벡터 = 근거 지지도(축마다 0.9·0.6·0.3) + 선지 속 단어 효과의 합, 축마다 −1~1로 자른다.
0은 '지문에 근거 없음', +는 지문이 받침, −는 지문과 어긋남이다.
"""

import json
import math
from functools import cache
from pathlib import Path

DATA = Path(__file__).parent / "data" / "exam.json"
NUM = "①②③④⑤"
AXIS = {"x": 0, "y": 1, "z": 2}


@cache
def load() -> dict:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    effect = {e["kind"]: e["v"] for e in d["effects"]}
    for q in d["questions"]:
        for o in q["options"]:
            v = list(o["base"])
            for w in o["words"]:
                w["v"] = effect[w["kind"]]
                v[AXIS[w["axis"]]] += w["v"]
            o["vec"] = [round(max(-1.0, min(1.0, t)), 2) for t in v]
    return d


def cos(a, b) -> float:
    na = math.sqrt(sum(t * t for t in a))
    nb = math.sqrt(sum(t * t for t in b))
    return sum(i * j for i, j in zip(a, b)) / (na * nb) if na and nb else 0.0


def stats(q: dict, tau: float) -> dict:
    """정답 대비 코사인, 난도 지수 D, 가장 헷갈렸을 선지.

    D = Σ max(0, (cos − τ) / (1 − τ)) — 정답과 τ 넘게 닮은 오답이 많고(갯수) 더 닮을수록(정도) 커진다.
    """
    vs = [o["vec"] for o in q["options"]]
    a = vs[q["answer"] - 1]
    c = {i + 1: cos(a, v) for i, v in enumerate(vs) if i + 1 != q["answer"]}
    lift = {k: max(0.0, (x - tau) / (1 - tau)) for k, x in c.items()}
    top = max(c, key=lambda k: c[k])
    return {
        "cos": c,
        "D": sum(lift.values()),
        "N": sum(x >= tau for x in c.values()),
        "top": top,
        "top_cos": c[top],
    }


def axis_corr(d: dict) -> list[list[float]]:
    """50개 벡터에서 축끼리의 피어슨 상관 — 축 독립성 검사."""
    vs = [o["vec"] for q in d["questions"] for o in q["options"]]
    cols = list(zip(*vs))

    def r(a, b):
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        sab = sum((p - ma) * (s - mb) for p, s in zip(a, b))
        return sab / math.sqrt(sum((p - ma) ** 2 for p in a) * sum((s - mb) ** 2 for s in b))

    return [[r(cols[i], cols[j]) for j in range(3)] for i in range(3)]


DISTORT = ("반의", "치환", "층위")  # 지문과 어긋나게 만든 단어 = 판정 단서


def clues(d: dict) -> list[dict]:
    """판정 단서마다 내가 제대로 처리했는지.

    부정 발문은 단서가 든 정답을 골라야, 긍정 발문은 단서가 든 오답을 피해야 처리한 것이다.
    2번처럼 맞혔어도 지문 정의가 아닌 어감으로 맞힌 경우는 '운'으로 따로 센다.
    """
    out = []
    for q in d["questions"]:
        for i, o in enumerate(q["options"], 1):
            for w in o["words"]:
                if w["kind"] not in DISTORT:
                    continue
                ok = (q["mine"] == i) if i == q["answer"] else (q["mine"] != i)
                luck = ok and i == q["answer"] and outcome(q) == "운통과"
                out.append({"no": q["no"], "opt": i, "w": w["w"], "axis": w["axis"],
                            "kind": w["kind"], "ok": ok and not luck, "luck": luck, "miss": not ok})
    return out


def pulled(d: dict) -> list[dict]:
    """틀린 문항에서 내가 고른 선지에 든 단어 — 무엇에 끌려갔나."""
    return [
        {"no": q["no"], "opt": q["mine"], "w": w["w"], "axis": w["axis"], "kind": w["kind"], "v": w["v"]}
        for q in d["questions"] if q["mine"] != q["answer"]
        for w in q["options"][q["mine"] - 1]["words"]
    ]


def shake(d: dict, by: str) -> list[dict]:
    """축(by='axis') 또는 단어 종류(by='kind')별 흔들림률 = (놓침 + 운) / 단서 수."""
    groups: dict[str, list[dict]] = {}
    for c in clues(d):
        groups.setdefault(c[by], []).append(c)
    rows = []
    for k, cs in groups.items():
        miss = sum(c["miss"] for c in cs)
        luck = sum(c["luck"] for c in cs)
        rows.append({by: k, "clues": len(cs), "miss": miss, "luck": luck,
                     "rate": (miss + luck) / len(cs)})
    return sorted(rows, key=lambda r: (-r["rate"], -r["miss"]))


def outcome(q: dict) -> str:
    if q["mine"] != q["answer"]:
        return "오답"
    return "운통과" if q["no"] == 2 else "정답"
