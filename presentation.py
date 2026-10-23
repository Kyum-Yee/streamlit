"""발표 화면에 문제 원문과 원리 퀴즈를 일관되게 표시하는 자료를 만든다."""

import analysis as A


def _range_key(question_no: int, ranges: dict[str, str]) -> str | None:
    for key in ranges:
        start, end = (int(value) for value in key.split("-"))
        if start <= question_no <= end:
            return key
    return None


def question_material(exam: dict, question_no: int) -> dict:
    """문항 하나와 함께 읽어야 할 지문·보기를 돌려준다."""
    question = next((q for q in exam["questions"] if q["no"] == question_no), None)
    if question is None:
        raise ValueError(f"존재하지 않는 문항: {question_no}")

    passage_key = _range_key(question_no, exam["passages"])
    if passage_key is None:
        raise ValueError(f"{question_no}번에 연결된 지문이 없습니다.")
    box_key = _range_key(question_no, exam["boxes"])

    return {
        "passage": exam["passages"][passage_key],
        "box": exam["boxes"][box_key] if box_key else None,
        "stem": question["stem"],
        "options": [option["text"] for option in question["options"]],
    }


def option_stat_rows(question: dict) -> list[dict]:
    """선지 원문을 보존한 채 정답과의 코사인 유사도를 붙인다."""
    answer_vector = question["options"][question["answer"] - 1]["vec"]
    rows = []
    for option_no, option in enumerate(question["options"], 1):
        states = []
        if option_no == question["answer"]:
            states.append("정답")
        if option_no == question["mine"]:
            states.append("내 답")
        rows.append({
            "선지": A.NUM[option_no - 1],
            "선지 내용": option["text"],
            "표시": " · ".join(states) if states else "—",
            "정답과 cos": round(A.cos(answer_vector, option["vec"]), 2),
        })
    return rows


def answer_feedback(question: dict, picked: int | None) -> dict[str, str]:
    """사용자가 직접 푼 답을 채점하되 제출 전에는 정답을 감춘다."""
    if picked is None:
        return {"kind": "warning", "message": "답을 먼저 고르세요."}

    answer = A.NUM[question["answer"] - 1]
    if picked == question["answer"]:
        return {"kind": "success", "message": f"정답입니다. 정답은 {answer}입니다."}
    return {"kind": "error", "message": f"오답입니다. 정답은 {answer}입니다."}


def glossary() -> list[dict[str, str]]:
    """발표를 읽기 전에 필요한 용어의 짧은 정의."""
    return [
        {"용어": "선지", "정의": "문항에서 고르는 각각의 선택 문장."},
        {"용어": "벡터", "정의": "선지의 사실·관계·개념 근거를 (x, y, z) 세 값으로 나타낸 것."},
        {"용어": "근거 지지도", "정의": "지문이 선지를 얼마나 직접 받치는지 축마다 준 기본값."},
        {"용어": "단어 효과", "정의": "반의·치환·층위 같은 표현이 해당 축의 값을 깎는 정도."},
        {"용어": "코사인 유사도", "정의": "두 벡터의 방향이 얼마나 같은지 나타내는 −1~1의 값."},
        {"용어": "문턱 τ", "정의": "두 선지가 닮았다고 세기 시작하는 코사인 유사도 기준."},
        {"용어": "난도 지수 D", "정의": "정답과 문턱 이상 닮은 오답의 수와 닮은 정도를 합친 값."},
    ]


def example_dataset_rows(question: dict) -> list[dict]:
    """문항 하나를 선지 단위 데이터셋으로 펼쳐 정답과 내 답을 구분한다."""
    rows = []
    for option_no, option in enumerate(question["options"], 1):
        vector = ", ".join(f"{value:.2f}" for value in option["vec"])
        rows.append({
            "문항": f"{question['no']}번",
            "선지": A.NUM[option_no - 1],
            "선지 내용": option["text"],
            "벡터 (x, y, z)": f"({vector})",
            "정답": "✓" if option_no == question["answer"] else "",
            "내 답": "✓" if option_no == question["mine"] else "",
        })
    return rows


def principle_quiz() -> list[dict]:
    """개별 문항의 수치를 외우지 않고 모델의 원리를 적용하는 퀴즈."""
    return [
        {
            "concept": "코사인 유사도",
            "question": "두 선지 벡터의 길이는 다르지만 같은 방향을 가리킨다. 코사인 유사도는 어떻게 될까?",
            "choices": ["1에 가깝다", "0에 가깝다", "−1에 가깝다", "더 긴 벡터가 정답이 된다"],
            "answer": "1에 가깝다",
            "why": "코사인 유사도는 길이가 아니라 두 벡터가 이루는 각도를 비교한다. 같은 방향이면 1이다.",
        },
        {
            "concept": "난도 지수",
            "question": "다른 조건이 같을 때 난도 지수 D가 가장 커지는 경우는?",
            "choices": [
                "정답과 문턱 이상 닮은 오답이 많고, 유사도도 높을 때",
                "정답 벡터의 길이만 길 때",
                "모든 오답의 유사도가 문턱보다 낮을 때",
                "정답의 선지 번호가 뒤쪽일 때",
            ],
            "answer": "정답과 문턱 이상 닮은 오답이 많고, 유사도도 높을 때",
            "why": "D는 문턱을 넘은 오답의 수와 각 오답이 문턱을 넘어선 정도를 함께 더한다.",
        },
        {
            "concept": "벡터 축",
            "question": "선지 벡터의 한 축 값이 0이라는 말의 뜻은?",
            "choices": [
                "그 기준에서 지문 근거가 없다",
                "그 선지는 반드시 오답이다",
                "정답과 직각을 이룬다",
                "그 기준에서 지문과 완전히 반대다",
            ],
            "answer": "그 기준에서 지문 근거가 없다",
            "why": "각 축에서 0은 근거 없음, 양수는 지문이 받침, 음수는 지문과 어긋남을 뜻한다.",
        },
    ]
