"""Streamlit 화면에 요청한 사용자 흐름이 실제로 구성되는지 확인한다."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

import analysis as A


class AppSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app_path = Path(__file__).parents[1] / "main.py"
        cls.app = AppTest.from_file(str(app_path)).run(timeout=30)

    def test_app_builds_without_exception(self) -> None:
        self.assertEqual(list(self.app.exception), [])

    def test_first_tab_starts_with_a_solvable_exam_question(self) -> None:
        self.assertEqual(self.app.tabs[0].label, "⓪ 문제 풀기와 배경")
        self.assertEqual(self.app.header[0].value, "국어 모의고사 문제 풀기")
        self.assertEqual(self.app.selectbox[0].label, "풀 문항")
        self.assertEqual(self.app.radio[0].label, "답을 고르세요")
        self.assertEqual(self.app.button[0].label, "정답 확인")

    def test_background_axes_and_terms_are_visible_in_zero_tab(self) -> None:
        subheaders = [element.value for element in self.app.subheader]
        markdown = [element.value for element in self.app.markdown]

        self.assertIn("탐구 배경", subheaders)
        self.assertIn("세 축", subheaders)
        self.assertIn("용어 정의", subheaders)
        self.assertTrue(any("사실" in value and "관계" in value and "개념" in value for value in markdown))
        self.assertIn("예시 데이터셋 — 정답·내 답 포함", [element.label for element in self.app.expander])

    def test_analysis_has_question_selector_and_full_text_sections(self) -> None:
        self.assertEqual(self.app.selectbox[1].label, "문항 선택")
        markdown = [element.value for element in self.app.markdown]
        first_question = A.load()["questions"][0]
        self.assertIn("**문제 전문**", markdown)
        self.assertIn("**선지 텍스트와 통계**", markdown)
        self.assertIn(A.load()["passages"]["1-5"], markdown)
        self.assertIn(f"**1. {first_question['stem']}**", markdown)
        self.assertIn(f"① {first_question['options'][0]['text']}", markdown)
        self.assertIn(first_question["options"][0]["text"], markdown)

    def test_quiz_widgets_ask_the_three_principles(self) -> None:
        labels = [radio.label for radio in self.app.radio[1:]]

        self.assertEqual(len(labels), 3)
        self.assertTrue(any("코사인 유사도" in label for label in labels))
        self.assertTrue(any("난도 지수" in label for label in labels))
        self.assertTrue(any("벡터 축" in label for label in labels))

    def test_user_can_submit_an_answer_and_get_feedback(self) -> None:
        self.app.radio[0].set_value(5).run()
        self.app.button[0].click().run()
        messages = [element.value for element in self.app.success]

        self.assertIn("정답입니다. 정답은 ⑤입니다.", messages)


if __name__ == "__main__":
    unittest.main()
