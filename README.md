# GlowScript on Streamlit

Streamlit 페이지에서 VPython(GlowScript) 3D 시뮬레이션 코드를 고치고 바로 돌려 본다.

## 실행

```sh
uv sync
uv run streamlit run main.py
```

이 폴더 하나로 완결된다. Python 3.13(`.python-version`), 의존성은 `pyproject.toml`과 `uv.lock`이 정한다.

## 구조

| 파일 | 역할 |
|---|---|
| `main.py` | 페이지: 예제 선택, 코드 편집기, ▶ 실행, 3D 장면 |
| `glowscript_view.py` | 코드 한 편을 실행하는 iframe HTML을 만든다 |
| `scenes/*.py` | 예제. `.py`를 넣으면 목록에 뜨고, 이름은 코드의 `scene.title` |

## 동작

- 컴파일과 렌더는 보는 사람의 브라우저가 맡는다. glowscript.org의 GlowScript 라이브러리를 불러 Python을 JS로 바꿔 돌리므로, 서버에는 `vpython` 패키지가 필요 없고 인터넷 연결은 필요하다.
- 기본판은 3.2(최신)다. 첫 줄에 `Web VPython 3.1`처럼 적으면 그 판으로 돈다(2.9 이상).
- 언어는 glowscript.org와 같은 브라우저 Python(RapydScript)이다. `numpy` 같은 외부 패키지는 쓸 수 없다.
- 편집 중에는 다시 그리지 않는다. ▶ 실행 또는 ⌘/Ctrl+Enter로 돌린다.
- 오류는 장면 자리에 편집기 기준 줄 번호와 함께 뜬다. 전체 스택은 브라우저 개발자 도구 콘솔에 있다.
- 키보드를 쓰는 장면(장애물 피하기)은 장면을 한 번 클릭해야 키가 먹는다.

## 배포 (Streamlit Community Cloud)

저장소 `Kyum-Yee/streamlit`, 브랜치 `master`, 메인 파일 `main.py`. Cloud가 `uv.lock`을 읽어 설치한다. Python 판은 배포 설정에서 3.13을 고른다.
