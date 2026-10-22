"""발표: 헷갈리는 선지는 정답과 닮았을까? — VPython 선지 벡터로 본 국어 모의고사 10문항.

실행: uv run streamlit run main.py
"""

import altair as alt
import pandas as pd
import streamlit as st

import analysis as A
import sim
from glowscript_view import build_html

SECTIONS = ["① 탐구 질문", "② 시뮬레이션", "③ 원리", "④ 결과 분석", "⑤ 결론과 한계", "⑥ 퀴즈"]
RESULT_COLOR = {"오답": "#d64545", "운통과": "#f0a020", "정답": "#9aa3ad"}

st.set_page_config(page_title="선지 벡터 탐구 발표", page_icon="🧭", layout="wide")

d = A.load()
TAU = d["tau"]
Q = {q["no"]: q for q in d["questions"]}


def n(i: int) -> str:
    return A.NUM[i - 1]


def table(tau: float) -> pd.DataFrame:
    rows = []
    for q in d["questions"]:
        s = A.stats(q, tau)
        rows.append({
            "문항": f"{q['no']}번",
            "발문": "부정" if q["negative"] else "긍정",
            "정답": n(q["answer"]),
            "내 답": n(q["mine"]),
            "결과": A.outcome(q),
            "가장 헷갈렸을 선지": n(s["top"]),
            "정답과 cos": round(s["top_cos"], 2),
            "τ 넘는 오답": s["N"],
            "난도 지수 D": round(s["D"], 2),
        })
    return pd.DataFrame(rows)


# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("### 발표자")
    st.markdown("**Kyum-Yee**")
    st.markdown("분야: 국어 · 벡터")
    st.divider()
    st.markdown("### 발표 순서")
    for s in SECTIONS:
        st.markdown(s)

st.title("헷갈리는 선지는 정답과 닮았을까?")
st.caption("VPython 3차원 벡터로 본 2026-10-21 국어 모의고사 10문항")

tabs = st.tabs(SECTIONS)

# ---------- ① 탐구 질문 ----------
with tabs[0]:
    st.header("탐구 질문")
    wrong = [q["no"] for q in d["questions"] if q["mine"] != q["answer"]]
    st.markdown(
        f"10월 21일 국어 모의고사(독서 「기후 되먹임과 이산화탄소의 복사 강제력」, 고전소설 「배시황전」) "
        f"10문항에서 7문항을 맞혔습니다. 틀린 {'·'.join(map(str, wrong))}번은 모두 "
        "「적절하지 않은 것」을 고르는 문항이었고, 세 번 모두 지문과 맞는 선지를 틀렸다고 골랐습니다."
    )
    st.markdown(
        "- 내가 고른 오답은 정답과 **무엇이** 닮았을까?\n"
        "- 정답과 닮은 선지가 **많고 더 닮을수록** 문제가 어려울까?"
    )
    st.info("가설: 정답과 코사인 유사도가 큰 선지가 많을수록, 그리고 그 유사도가 클수록 문제가 어렵다.")
    st.dataframe(
        table(TAU)[["문항", "발문", "정답", "내 답", "결과"]].set_index("문항").T,
        width="stretch",
    )

# ---------- ② 시뮬레이션 ----------
with tabs[1]:
    st.header("시뮬레이션")
    st.markdown(
        "문항을 고른 뒤 선지를 켜고 끄며 정답(주황)·내 답(빨강)·가장 헷갈렸을 선지(★)를 비교해 보세요. "
        "켠 선지 n개의 코사인 유사도는 화면 아래 콘솔에 나옵니다. 화면을 끌면 돌아갑니다."
    )
    source = sim.build_source(d)
    st.iframe(build_html(source), height="content", alt="문항별 선지 벡터 3D 시뮬레이션")
    with st.expander("VPython 코드"):
        st.caption("glowscript.org에 그대로 붙여 넣어도 돈다.")
        st.code(source, language="python")
        st.download_button("코드 내려받기", source, file_name="option_vectors.py", mime="text/x-python")

# ---------- ③ 원리 ----------
with tabs[2]:
    st.header("원리")
    st.markdown(
        "선지를 지문과 대조하는 세 기준을 축으로 삼았습니다. 0은 '지문에 근거 없음', "
        "+는 지문이 받침, −는 지문과 어긋남입니다."
    )
    st.table(pd.DataFrame(
        [{"축": f"{a['key']} {a['name']}", "묻는 것": a["q"]} for a in d["axes"]]
    ).set_index("축"))

    st.subheader("벡터 = 근거 지지도 + 단어 효과")
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown("**근거 지지도** — 축마다, 지문이 얼마나 가까이서 받치나")
        st.table(pd.DataFrame(
            [{"단계": s["name"], "값": f"+{s['v']:.2f}", "뜻": s["q"]} for s in d["support"]]
        ).set_index("단계"))
    with c2:
        st.markdown("**단어 효과** — 선지 속 단어 하나가 그 축을 얼마나 깎나")
        st.table(pd.DataFrame(
            [{"종류": e["kind"], "값": f"{e['v']:.2f}", "뜻": e["q"]} for e in d["effects"]]
        ).set_index("종류"))
    st.markdown(
        "부정어가 들었다고 곧바로 −가 되지 않습니다. 정반대 말(−1.50)과 뜻은 지문과 같은 부정(−0.30)을 "
        "단계로 나눠 깎고, 합한 값은 축마다 −1~1로 자릅니다."
    )
    o = Q[7]["options"][4]
    steps = " ".join(f"+ 「{w['w']}」 {w['kind']} {w['axis']} {w['v']:.2f}" for w in o["words"])
    vec = ", ".join(f"{t:.2f}" for t in o["vec"])
    base = ", ".join(f"{t:.2f}" for t in o["base"])
    st.markdown(f"예: 7번 ⑤ = 지지도 ({base}) {steps} = **({vec})**")

    st.subheader("코사인 유사도와 난도 지수")
    st.latex(r"\cos\theta = \frac{\vec a \cdot \vec b}{|\vec a|\,|\vec b|}")
    st.latex(
        r"D = \sum_{i \ne \text{정답}} \max\!\left(0,\ \frac{\cos\theta_i - \tau}{1 - \tau}\right),"
        r"\quad \tau = " + f"{TAU:.2f}"
    )
    st.markdown(
        "D는 정답과 τ 넘게 닮은 오답의 **갯수**와 넘어선 **정도**를 함께 셉니다. "
        "τ = 0.70은 두 벡터 사이 각이 약 46° 안쪽이라는 뜻입니다."
    )

    st.subheader("축은 서로 독립인가")
    r = A.axis_corr(d)
    names = [f"{a['key']} {a['name']}" for a in d["axes"]]
    st.table(pd.DataFrame([[f"{v:.2f}" for v in row] for row in r], index=names, columns=names))
    off = max(abs(r[i][j]) for i in range(3) for j in range(3) if i != j)
    st.caption(f"50개 선지 벡터에서 축끼리의 피어슨 상관. 대각선 밖 최대 |r| = {off:.2f}로, 한 축이 다른 축을 거의 설명하지 못한다.")

# ---------- ④ 결과 분석 ----------
with tabs[3]:
    st.header("결과 분석")
    tau = st.slider("τ (닮았다고 볼 코사인 문턱)", 0.50, 0.90, TAU, 0.05)
    df = table(tau)
    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("문항:N", sort=None, title=None),
            y=alt.Y("난도 지수 D:Q", title="난도 지수 D"),
            color=alt.Color("결과:N", scale=alt.Scale(domain=list(RESULT_COLOR), range=list(RESULT_COLOR.values())),
                            legend=alt.Legend(orient="top", title=None)),
            tooltip=["문항", "결과", "가장 헷갈렸을 선지", alt.Tooltip("난도 지수 D:Q", format=".2f")],
        )
        .properties(height=280)
    )
    text = chart.mark_text(dy=-8, fontSize=12).encode(text=alt.Text("난도 지수 D:Q", format=".2f"), color=alt.value("#333"))
    st.altair_chart(chart + text, width="stretch")

    top3 = df.sort_values("난도 지수 D", ascending=False).head(3)["문항"].tolist()
    wrong = df[df["결과"] == "오답"]
    hit = (wrong["가장 헷갈렸을 선지"] == wrong["내 답"]).sum()
    st.markdown(
        f"- τ = {tau:.2f}에서 D 상위 세 문항은 **{', '.join(top3)}**입니다. 실제로 틀린 문항은 "
        f"**{', '.join(wrong['문항'])}**입니다.\n"
        f"- 틀린 세 문항에서 '가장 헷갈렸을 선지'가 실제로 고른 답과 같았던 것은 **{hit}/{len(wrong)}**입니다.\n"
        "- 운으로 맞힌 2번은 틀린 문항 다음으로 D가 큽니다."
    )
    st.dataframe(df.set_index("문항").style.format({"정답과 cos": "{:.2f}", "난도 지수 D": "{:.2f}"}), width="stretch")

    # ---------- 어느 축에 흔들리나 ----------
    st.subheader("나는 어느 축에 흔들리나")
    st.markdown(
        "선지 속 오류 단어(반의·치환·층위)를 **판정 단서**로 보고, 단서마다 제대로 처리했는지 셉니다. "
        "부정 발문은 단서가 든 정답을 골라야, 긍정 발문은 단서가 든 오답을 피해야 처리한 것입니다. "
        "흔들림률 = (놓친 단서 + 운으로 넘긴 단서) / 단서 수."
    )
    AXN = {a["key"]: f"{a['key']} {a['name']}" for a in d["axes"]}
    by_axis = pd.DataFrame([
        {"축": AXN[r["axis"]], "단서": r["clues"], "놓침": r["miss"], "운": r["luck"], "흔들림률": round(r["rate"], 2)}
        for r in A.shake(d, "axis")
    ])
    by_kind = pd.DataFrame([
        {"단어 종류": r["kind"], "단서": r["clues"], "놓침": r["miss"], "운": r["luck"], "흔들림률": round(r["rate"], 2)}
        for r in A.shake(d, "kind")
    ])
    c1, c2 = st.columns(2)
    with c1:
        bar = (
            alt.Chart(by_axis)
            .mark_bar(cornerRadiusEnd=3, color="#d64545")
            .encode(x=alt.X("흔들림률:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format=".2f")),
                    y=alt.Y("축:N", sort="-x", title=None),
                    tooltip=["축", "단서", "놓침", "운", alt.Tooltip("흔들림률:Q", format=".2f")])
            .properties(height=150, title="축별 흔들림률")
        )
        st.altair_chart(bar + bar.mark_text(align="left", dx=4).encode(text=alt.Text("흔들림률:Q", format=".2f"), color=alt.value("#333")),
                        width="stretch")
        st.dataframe(by_axis.set_index("축").style.format({"흔들림률": "{:.2f}"}), width="stretch")
    with c2:
        st.markdown("**단어 종류별**")
        st.dataframe(by_kind.set_index("단어 종류").style.format({"흔들림률": "{:.2f}"}), width="stretch")
        missed = [c for c in A.clues(d) if c["miss"] or c["luck"]]
        st.markdown("**놓친 단서**")
        st.markdown("\n".join(
            f"- {c['no']}번 {n(c['opt'])} 「{c['w']}」 {AXN[c['axis']]} · {c['kind']}{' (운으로 넘김)' if c['luck'] else ''}"
            for c in missed
        ))

    pull = A.pulled(d)
    pull_axis = pd.Series([AXN[p["axis"]] for p in pull]).value_counts()
    st.markdown(
        "**끌려간 선지에 든 단어** — 틀린 문항에서 내가 고른 참 선지는 어떤 단어 때문에 거짓처럼 보였나: "
        + ", ".join(f"{p['no']}번 {n(p['opt'])} 「{p['w']}」({p['kind']} {AXN[p['axis']]} {p['v']:.2f})" for p in pull)
        + f". 축별로는 {', '.join(f'{k} {v}개' for k, v in pull_axis.items())}."
    )
    worst_axis, worst_kind = A.shake(d, "axis")[0], A.shake(d, "kind")[0]
    st.success(
        f"가장 흔들리는 축은 **{AXN[worst_axis['axis']]}**(흔들림률 {worst_axis['rate']:.2f})이고, "
        f"단어 종류로는 **{worst_kind['kind']}**(흔들림률 {worst_kind['rate']:.2f}, 단서 {worst_kind['clues']}개 중 "
        f"{worst_kind['miss']}개 놓침)입니다."
    )

# ---------- ⑤ 결론과 한계 ----------
with tabs[4]:
    s7, s5, s9 = (A.stats(Q[k], TAU) for k in (7, 5, 9))
    st.header("결론")
    st.markdown(
        f"가설대로 정답과 닮은 선지가 많고 더 닮은 문항일수록 어려웠습니다. 난도 지수 D 상위 세 문항"
        f"(7번 {s7['D']:.2f}, 5번 {s5['D']:.2f}, 9번 {s9['D']:.2f})이 실제로 틀린 세 문항과 같고, "
        "τ를 0.50에서 0.90까지 바꿔도 이 순서는 유지됩니다. 틀린 문항에서는 정답과 가장 닮은 선지를 골랐습니다."
    )
    st.markdown(
        "닮음은 대부분 **개념(z) 축**에서 생겼습니다. 정답이 「기준」「두었다고」「㉯에」처럼 층위만 옮긴 말로 "
        "z가 조금 깎였을 때, 가정·반사실·해석으로 z가 비슷하게 낮은 참 선지가 정답 옆에 붙었습니다."
    )
    wa, wk = A.shake(d, "axis")[0], A.shake(d, "kind")[0]
    st.markdown(
        f"축별 통계로 보면 내가 흔들리는 곳은 **{wa['axis']} 개념** 축 하나입니다(흔들림률 {wa['rate']:.2f}, "
        f"사실·관계 축은 0.00). 그중 **{wk['kind']} 이동** 단서는 {wk['clues']}개 중 {wk['miss']}개를 놓쳤습니다. "
        "정반대 말(반의)이나 다른 값(치환)은 거의 다 잡아냈습니다."
    )
    st.header("모델의 한계")
    st.markdown(
        "- 근거 지지도와 단어 효과는 사람이 매겼고, 매긴 사람이 결과를 이미 알고 있었다. 결과를 모른 채 매긴 새 세트로 다시 확인해야 한다.\n"
        "- 10문항, 한 사람의 기록이다. 문항별 풀이 시간이 없어 시간으로 본 난도와는 대조하지 못했다.\n"
        "- 세 축은 지문 대조만 본다. 2번처럼 지문 정의 대신 일상 어감(「상승 = 양」)으로 맞힌 경로는 담지 못한다."
    )
    st.header("더 알아보고 싶은 점")
    st.markdown("다음 모의고사에서 풀기 **전에** D를 먼저 계산해 두면, 틀릴 문항을 미리 맞힐 수 있을까?")

# ---------- ⑥ 퀴즈 ----------
with tabs[5]:
    st.header("퀴즈")
    quiz = [
        ("7번에서 정답 ⑤와 코사인 유사도가 1.00인 선지는?", ["①", "②", "③", "④"], "③",
         "③과 ⑤는 둘 다 (0.60, 0.60, −0.10)이라 방향이 같다. 실제로 고른 답도 ③이었다."),
        ("τ = 0.70에서 난도 지수 D가 가장 큰 문항은?", ["2번", "5번", "7번", "9번"], "7번",
         f"7번 D = {s7['D']:.2f}로, τ를 넘는 오답이 {s7['N']}개다."),
        ("「살아남지 못했으리라」처럼 부정어가 들었지만 뜻은 지문과 같은 말은 그 축을 얼마나 깎을까?",
         ["−1.50", "−0.70", "−0.30", "0"], "−0.30",
         "완전 부정이지만 지문과 어긋나지 않으므로 −0.30만 깎는다. 정반대 말은 −1.50이다."),
    ]
    for i, (q, choices, ans, why) in enumerate(quiz):
        pick = st.radio(f"Q{i + 1}. {q}", choices, index=None, key=f"quiz{i}", horizontal=True)
        if pick is not None:
            if pick == ans:
                st.success(f"정답! {why}")
            else:
                st.error("다시 생각해 보세요.")
