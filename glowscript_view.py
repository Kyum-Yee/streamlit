"""VPython 코드를 브라우저 안에서 GlowScript로 컴파일·실행하는 iframe HTML을 만든다.

서버는 HTML만 건네고, 컴파일·렌더는 보는 사람 브라우저가 glowscript.org 라이브러리로 한다.
그래서 이 앱 쪽에는 vpython 패키지도, 별도 렌더 서버도 필요 없다.
"""

import json
import re

CDN = "https://www.glowscript.org"
DEFAULT_VERSION = "3.2"

# glowscript.org 에디터의 첫 줄 표기: "Web VPython 3.2", "GlowScript 3.2 VPython"
_HEADER = re.compile(r"^\s*(?:web\s*vpython|glowscript)\s+(\d+\.\d+)\b", re.IGNORECASE)


def split_header(code: str) -> tuple[str, str, int]:
    """첫 줄 버전 표기를 떼어 (버전, 본문, 뗀 줄 수)를 돌려준다. 표기가 없으면 기본 버전."""
    lines = code.lstrip("﻿").replace("\r\n", "\n").split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        m = _HEADER.match(line)
        if m:
            return m.group(1), "\n".join(lines[i + 1 :]), i + 1
        break
    return DEFAULT_VERSION, "\n".join(lines), 0


def _js(value) -> str:
    """<script> 안에 넣을 JS 리터럴. '</script>'가 태그를 닫지 못하게 '</'를 끊는다."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_html(code: str, nonce: int = 0) -> str:
    """코드 한 편을 실행하는 완결된 HTML 문서. nonce가 바뀌면 같은 코드도 새로 실행된다."""
    version, body, offset = split_header(code)
    # 3.2 이후 판도 jQuery는 2.1 묶음을 쓴다(glowscript.org run.js 규칙)
    return f"""<!doctype html>
<!-- run {nonce} -->
<html lang="ko">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{CDN}/css/redmond/2.1/jquery-ui.custom.css">
<link rel="stylesheet" href="{CDN}/css/ide.css">
<style>
  html, body {{ margin: 0; background: #fff; color: #222;
    font: 14px/1.5 -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; }}
  #status {{ padding: 12px 4px; color: #777; }}
  #error {{ margin: 8px 0; padding: 10px 12px; border-left: 3px solid #c62828;
    background: #fdecea; color: #8e0000; white-space: pre-wrap;
    font: 13px/1.5 ui-monospace, Menlo, monospace; }}
</style>
<script src="{CDN}/lib/jquery/2.1/jquery.min.js"></script>
<script src="{CDN}/lib/jquery/2.1/jquery-ui.custom.min.js"></script>
<script src="{CDN}/package/glow.{version}.min.js"></script>
<script src="{CDN}/package/RScompiler.{version}.min.js"></script>
</head>
<body>
<div id="status">GlowScript {version} 불러오는 중…</div>
<div id="glowscript" class="glowscript"></div>
<pre id="error" hidden></pre>
<script>
(async function () {{
  const SOURCE = {_js(body)};
  const VERSION = {_js(version)};
  const OFFSET = {offset};          // 떼어 낸 버전 줄 수: 편집기 줄 번호로 되돌린다
  let program = "";
  const status = document.getElementById("status");
  const box = document.getElementById("error");

  // 컴파일된 JS 줄에 박힌 "N"; 표시를 거슬러 찾아 파이썬 줄 번호로 바꾼다
  function pyLine(err) {{
    const lines = program.split("\\n");
    const frames = String(err && err.stack || "").split("\\n");
    for (const f of frames) {{
      const m = f.match(/<anonymous>:(\\d+):(\\d+)/);
      if (!m) continue;
      for (let j = Number(m[1]) - 1, col = Number(m[2]); j >= 0; j--, col = Infinity) {{
        if (j >= lines.length) break;   // 컴파일된 프로그램 밖(라이브러리)의 프레임
        const hit = [...lines[j].slice(0, col).matchAll(/"(\\d+)";/g)].pop();
        if (hit) return Number(hit[1]);
      }}
    }}
    return null;
  }}

  function fail(kind, err) {{
    console.error(err);               // 전체 스택은 브라우저 개발자 도구에
    if (status) status.remove();
    let msg = String(err && err.message || err);
    let n = null;
    const m = msg.match(/ at line (\\d+): /);
    if (m) {{
      n = Number(m[1]);
      msg = msg.slice(0, m.index);
    }} else if (kind === "실행 오류") {{
      n = pyLine(err);
    }} else {{                          // 컴파일러 문구 속 "line N"도 편집기 줄 번호로
      msg = msg.replace(/line (\\d+)/, (_, d) => "line " + (Number(d) + OFFSET));
    }}
    const src = (window.__original && window.__original.text) || SOURCE.split("\\n");
    let where = "";
    if (n) where = "\\n\\n" + (n + OFFSET) + "번째 줄: " + (src[n - 1] || "").trim();
    box.textContent = kind + "\\n" + msg + where;
    box.hidden = false;
  }}

  if (typeof window.glowscript_compile !== "function") {{
    fail("GlowScript 라이브러리를 불러오지 못했습니다.", "glowscript.org 연결을 확인하세요.");
    return;
  }}
  try {{
    program = window.glowscript_compile(SOURCE, {{ lang: "vpython", version: VERSION, run: true }});
  }} catch (err) {{
    fail("컴파일 오류", err);
    return;
  }}
  status.remove();
  const container = $("#glowscript");
  container.removeAttr("id");
  window.__context = {{ glowscript_container: container }};
  window.__program = program;
  window.__reportScriptError = (err) => fail("실행 오류", err);  // canvas 이벤트 콜백의 오류
  try {{
    // 간접 eval: 전역 범위에서 돌려, 이 함수의 지역 이름이 box·status 같은 VPython 이름을 가리지 않게 한다
    window.userMain = (0, eval)(program);
    await window.userMain((err) => {{ if (err) fail("실행 오류", err); }});
  }} catch (err) {{
    fail("실행 오류", err);
  }}
}})();
</script>
</body>
</html>
"""
