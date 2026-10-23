"""문항별 선지 벡터를 그리는 VPython(GlowScript) 코드를 만든다.

데이터는 analysis.py가 계산한 값을 코드 맨 위 DATA에 박아 넣는다. 그래서 만들어진 코드는
glowscript.org에 그대로 붙여 넣어도 돈다.
"""

import analysis as A


def _data(d: dict) -> list:
    out = []
    for q in d["questions"]:
        s = A.stats(q, d["tau"])
        out.append({
            "no": q["no"],
            "stem": q["stem"],
            "answer": q["answer"],
            "mine": q["mine"],
            "result": A.outcome(q),
            "D": round(s["D"], 2),
            "N": s["N"],
            "top": s["top"],
            "opts": [
                {
                    "text": o["text"],
                    "vec": o["vec"],
                    "words": [[w["w"], w["axis"], w["kind"], w["v"]] for w in o["words"]],
                }
                for o in q["options"]
            ],
        })
    return out


def build_source(d: dict) -> str:
    axes = [[a["key"], a["name"]] for a in d["axes"]]
    return (
        "Web VPython 3.2\n\n"
        "# 2026-10-21 국어 10문항 · 선지 벡터 (analysis.py가 계산한 값)\n"
        f"DATA = {_data(d)!r}\n"
        f"AXES = {axes!r}\n"
        f"TAU = {d['tau']!r}\n"
        + _BODY
    )


_BODY = r'''
NUM = ["①", "②", "③", "④", "⑤"]
PALETTE = [vec(0.25, 0.45, 0.85), vec(0.10, 0.60, 0.55), vec(0.55, 0.35, 0.80),
           vec(0.45, 0.45, 0.50), vec(0.20, 0.65, 0.90)]
GOLD = vec(0.95, 0.62, 0.05)     # 정답
RED = vec(0.88, 0.18, 0.22)      # 내가 고른 오답

# ---------- ① 무대 ----------
scene.title = """
<h2>선지 벡터 시뮬레이션</h2>
<p>제작: Kyum-Yee | 주제: 헷갈리는 선지는 정답과 닮았을까?<br>
<span style="color:#777">화면을 끌면 돌아가고, 휠로 확대한다.</span></p>
"""
scene.width = 820
scene.height = 460
scene.background = color.white
scene.center = vec(0, 0, 0)
scene.forward = vec(-0.62, -0.42, -1)
scene.range = 1.55
scene.ambient = color.gray(0.55)

def V(l):
    return vec(l[0], l[1], l[2])

def f2(v):
    return "{:.2f}".format(v)

def cosine(a, b):
    if mag(a) == 0 or mag(b) == 0:
        return 0
    return dot(a, b) / (mag(a) * mag(b))

# 축 셋: −1 ~ +1, 끝에 이름. 0은 '지문에 근거 없음'
AX_DIR = [vec(1, 0, 0), vec(0, 1, 0), vec(0, 0, 1)]
for i in range(3):
    d = AX_DIR[i]
    arrow(pos=-1.15 * d, axis=2.3 * d, shaftwidth=0.008, headwidth=0.03, headlength=0.06,
          color=color.gray(0.55))
    label(pos=1.24 * d, text=AXES[i][0] + " " + AXES[i][1], box=False, height=13,
          color=color.gray(0.3))
    label(pos=-1.2 * d, text="−", box=False, height=12, color=color.gray(0.5))

# 정육면체 [−1, 1]³ 테두리: 깊이를 읽는 눈금
corners = []
for x in [-1, 1]:
    for y in [-1, 1]:
        for z in [-1, 1]:
            corners.append(vec(x, y, z))
for a in corners:
    for b in corners:
        if mag(a - b) == 2 and a.x + a.y + a.z < b.x + b.y + b.z:
            curve(pos=[a, b], color=color.gray(0.88), radius=0.002)
sphere(pos=vec(0, 0, 0), radius=0.018, color=color.gray(0.4))

# ---------- ② 선지 화살표 5개 (문항을 바꾸면 값만 바꾼다) ----------
arrows = []
tags = []
for i in range(5):
    arrows.append(arrow(pos=vec(0, 0, 0), axis=vec(0, 0, 0), shaftwidth=0.035,
                        headwidth=0.08, headlength=0.1, color=PALETTE[i]))
    tags.append(label(pos=vec(0, 0, 0), text=NUM[i], box=False, height=15,
                      color=PALETTE[i], opacity=0, line=False))
arc = curve(color=GOLD, radius=0.006)

state = {"q": 0, "grow": 1.0, "on": [True, True, True, True, True]}

# ---------- ③ 조작부 ----------
def pick_q(m):
    show_question(m.index)

def step(k):
    show_question((state["q"] + k + len(DATA)) % len(DATA))

def toggle(c):
    for i in range(5):
        if boxes[i] == c:
            state["on"][i] = c.checked
    refresh()

def all_on(b):
    for i in range(5):
        boxes[i].checked = True
        state["on"][i] = True
    refresh()

def key_only(b):
    q = DATA[state["q"]]
    for i in range(5):
        keep = (i + 1 == q["answer"]) or (i + 1 == q["mine"]) or (i + 1 == q["top"])
        boxes[i].checked = keep
        state["on"][i] = keep
    refresh()

scene.append_to_caption("\n<b>문항</b> ")
def prev_q(b):
    step(-1)

def next_q(b):
    step(1)

def redraw(c):
    refresh()

button(text=" ◀ ", bind=prev_q)
qmenu = menu(choices=["{}번 · {}".format(q["no"], q["result"]) for q in DATA], bind=pick_q)
button(text=" ▶ ", bind=next_q)
scene.append_to_caption("   ")
mark = checkbox(text="정답·내 답 강조 ", checked=True, bind=redraw)
conf = checkbox(text="가장 헷갈렸을 선지 ", checked=True, bind=redraw)
scene.append_to_caption("\n<b>선지 켜고 끄기</b> ")
boxes = []
for i in range(5):
    boxes.append(checkbox(text=NUM[i] + " ", checked=True, bind=toggle))
button(text="모두 켜기", bind=all_on)
scene.append_to_caption(" ")
button(text="정답·내 답·헷갈림만", bind=key_only)
scene.append_to_caption("\n")
console = wtext(text="")

# ---------- ④ 화면과 콘솔 갱신 ----------
def role(q, i):
    if i == q["answer"] and i == q["mine"]:
        return "정답 = 내 답"
    if i == q["answer"]:
        return "정답"
    if i == q["mine"]:
        return "내 답"
    return ""

def colour(q, i):
    if mark.checked and i == q["answer"]:
        return GOLD
    if mark.checked and i == q["mine"]:
        return RED
    return PALETTE[i - 1]

def refresh():
    q = DATA[state["q"]]
    g = state["grow"]
    a_vec = V(q["opts"][q["answer"] - 1]["vec"])
    seen = []
    for i in range(1, 6):
        v = V(q["opts"][i - 1]["vec"])
        on = state["on"][i - 1]
        arrows[i - 1].visible = on
        tags[i - 1].visible = on
        arrows[i - 1].axis = v * g
        arrows[i - 1].color = colour(q, i)
        # 같은 자리에 겹친 화살표는 이름표를 위로 비켜 둔다
        shift = 0
        for s in seen:
            if mag(s - v) < 0.05:
                shift += 1
        seen.append(v)
        tip = v * g
        out = norm(tip) * 0.09 if mag(tip) > 0 else vec(0, 0, 0)
        tags[i - 1].pos = tip + out
        tags[i - 1].yoffset = 16 * shift
        t = NUM[i - 1]
        r = role(q, i) if mark.checked else ""
        if r != "":
            t = t + " " + r
        if conf.checked and i == q["top"]:
            t = t + " ★"
        tags[i - 1].text = t
        tags[i - 1].color = colour(q, i)
    # 정답 → 가장 헷갈렸을 선지 사이 각을 호로 잇는다
    arc.clear()
    b_vec = V(q["opts"][q["top"] - 1]["vec"])
    if conf.checked and state["on"][q["answer"] - 1] and state["on"][q["top"] - 1]:
        for k in range(21):
            p = norm(a_vec * (1 - k / 20) + b_vec * (k / 20))
            arc.append(p * 0.45 * g)
    write_console(q)

def write_console(q):
    on = [i for i in range(1, 6) if state["on"][i - 1]]
    a_vec = V(q["opts"][q["answer"] - 1]["vec"])
    s = "<style>.gsc td{padding:2px 14px 2px 0;white-space:nowrap}.gsc td.w{white-space:normal}</style>"
    s += "<div style='font-family:Menlo,monospace;font-size:13px;line-height:1.55;"
    s += "background:#1e1f24;color:#e8e8e8;padding:12px 14px;border-radius:8px;max-width:796px;"
    s += "white-space:normal'>"
    s += "<span style='color:#9aa0a6'>&gt;&gt;&gt; {}번 · {}</span><br>".format(q["no"], q["stem"])
    s += "정답 <b style='color:#f5a623'>{}</b> · 내 답 <b style='color:{}'>{}</b> · 결과 {}<br><br>".format(
        NUM[q["answer"] - 1], "#ff6b6b" if q["mine"] != q["answer"] else "#f5a623",
        NUM[q["mine"] - 1], q["result"])
    s += "<table class='gsc' style='border-collapse:collapse;color:#e8e8e8;font-size:12.5px'>"
    s += "<tr style='color:#9aa0a6'><td>선지</td><td>x 사실</td><td>y 관계</td><td>z 개념</td>"
    s += "<td>cos(정답)</td><td>단어 효과</td></tr>"
    for i in range(1, 6):
        o = q["opts"][i - 1]
        v = V(o["vec"])
        c = "—" if i == q["answer"] else f2(cosine(a_vec, v))
        # 컴프리헨션 안에서 사용자 함수를 부르면 GlowScript가 깨지므로 반복문으로 모은다
        parts = []
        for w in o["words"]:
            parts.append("{} {} {}{}".format(w[0], w[2], w[1], f2(w[3])))
        words = ", ".join(parts)
        dim = "" if state["on"][i - 1] else "opacity:0.4;"
        mark_t = ""
        if i == q["answer"]:
            mark_t = " 정답"
        elif i == q["mine"]:
            mark_t = " 내 답"
        if i == q["top"]:
            mark_t += " ★"
        s += "<tr style='{}'><td>{}{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>".format(
            dim, NUM[i - 1], mark_t, f2(o["vec"][0]), f2(o["vec"][1]), f2(o["vec"][2]), c)
        s += "<td class='w' style='color:#b5bac1'>{}</td></tr>".format(words if words else "—")
    s += "</table><br>"
    # 켠 선지 n개의 코사인 유사도
    if len(on) >= 2:
        s += "<b>켠 선지 {}개의 코사인 유사도</b><br>".format(len(on))
        s += "<table class='gsc' style='border-collapse:collapse;color:#e8e8e8;font-size:12.5px'><tr><td></td>"
        for j in on:
            s += "<td>{}</td>".format(NUM[j - 1])
        s += "</tr>"
        total = 0
        pairs = 0
        for i in on:
            s += "<tr><td>{}</td>".format(NUM[i - 1])
            for j in on:
                c = cosine(V(q["opts"][i - 1]["vec"]), V(q["opts"][j - 1]["vec"]))
                hot = "color:#f5a623;" if (i != j and c >= TAU) else ""
                s += "<td style='{}'>{}</td>".format(hot, f2(c))
                if i < j:
                    total += c
                    pairs += 1
            s += "</tr>"
        s += "</table>평균(쌍 {}개) {}<br><br>".format(pairs, f2(total / pairs))
    else:
        s += "<span style='color:#9aa0a6'>선지를 2개 이상 켜면 코사인 유사도 표가 나온다.</span><br><br>"
    top = q["top"]
    t_vec = V(q["opts"][top - 1]["vec"])
    s += "<b>가장 헷갈렸을 선지</b> {} — 정답과 cos {}".format(NUM[top - 1], f2(cosine(a_vec, t_vec)))
    if top == q["mine"] and q["mine"] != q["answer"]:
        s += " · 실제로 고른 답"
    s += "<br><b>난도 지수</b> D = {} (τ = {} 넘는 오답 {}개)".format(f2(q["D"]), f2(TAU), q["N"])
    s += "</div>"
    console.text = s

def show_question(k):
    state["q"] = k
    qmenu.index = k
    state["grow"] = 0.0
    refresh()

show_question(0)

# ---------- ⑤ 문항을 바꾸면 화살표가 원점에서 자라난다 ----------
while True:
    rate(60)
    if state["grow"] < 1:
        state["grow"] = min(1, state["grow"] + 0.06)
        refresh()
'''
