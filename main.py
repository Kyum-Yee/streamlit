"""GlowScript(Web VPython) 3D 시뮬레이션을 Streamlit 페이지에서 편집·실행한다.

실행: uv run streamlit run main.py
"""

import re
from pathlib import Path

import streamlit as st

from glowscript_view import DEFAULT_VERSION, build_html

SCENES = Path(__file__).parent / "scenes"
BLANK = "빈 코드"
STARTER = """from vpython import *

ball = sphere(color=color.orange)
while True:
    rate(30)
    ball.rotate(angle=0.02, axis=vector(0, 1, 0))
"""


def scene_title(path: Path) -> str:
    """선택 목록에 띄울 이름: 코드의 scene.title, 없으면 파일 이름."""
    m = re.search(r'^scene\.title\s*=\s*["\'](.+?)["\']', path.read_text(encoding="utf-8"), re.MULTILINE)
    return m.group(1) if m else path.stem


@st.cache_data
def load_scenes() -> dict[str, str]:
    """{표시 이름: 코드}. scenes/ 에 .py를 넣으면 목록에 바로 뜬다."""
    return {scene_title(p): p.read_text(encoding="utf-8") for p in sorted(SCENES.glob("*.py"))}


def pick_scene():
    """예제를 고르면 편집기를 그 코드로 바꾸고 곧바로 실행한다."""
    name = st.session_state.scene
    code = STARTER if name == BLANK else load_scenes()[name]
    st.session_state.code = st.session_state.run_code = code
    st.session_state.nonce += 1


def run():
    st.session_state.run_code = st.session_state.code
    st.session_state.nonce += 1


st.set_page_config(page_title="GlowScript", page_icon="🪐", layout="wide")

scenes = load_scenes()
names = [*scenes, BLANK]
if "code" not in st.session_state:
    st.session_state.code = st.session_state.run_code = scenes[names[0]] if scenes else STARTER
    st.session_state.nonce = 0

with st.sidebar:
    st.selectbox("예제", names, key="scene", on_change=pick_scene)
    st.download_button(
        "코드 내려받기",
        st.session_state.code,
        file_name="scene.py",
        mime="text/x-python",
        width="stretch",
    )
    st.caption(
        f"GlowScript {DEFAULT_VERSION} · 첫 줄에 `Web VPython 3.1`처럼 적으면 그 판으로 돈다. "
        "키보드 장면은 화면을 한 번 클릭해야 키가 먹는다."
    )

st.title("GlowScript")
st.html("<style>.stTextArea textarea { font-family: ui-monospace, Menlo, monospace; tab-size: 4; }</style>")

# 폼 안의 편집은 실행 전까지 페이지를 다시 그리지 않는다. ⌘/Ctrl+Enter로도 실행된다.
with st.expander("코드", expanded=True), st.form("editor", border=False):
    st.text_area("VPython", key="code", height=360, label_visibility="collapsed")
    st.form_submit_button("▶ 실행", type="primary", on_click=run)

st.iframe(
    build_html(st.session_state.run_code, st.session_state.nonce),
    height="content",
    alt="GlowScript 3D 장면",
)
