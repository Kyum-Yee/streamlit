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

    def test_analysis_has_question_selector_and_full_text_sections(self) -> None:
        self.assertEqual(self.app.selectbox[0].label, "문항 선택")
        markdown = [element.value for element in self.app.markdown]
        first_question = A.load()["questions"][0]
        self.assertIn("**문제 전문**", markdown)
        self.assertIn("**선지 텍스트와 통계**", markdown)
        self.assertIn(A.load()["passages"]["1-5"], markdown)
        self.assertIn(f"**1. {first_question['stem']}**", markdown)
        self.assertIn(f"① {first_question['options'][0]['text']}", markdown)
        self.assertIn(first_question["options"][0]["text"], markdown)

    def test_quiz_widgets_ask_the_three_principles(self) -> None:
        labels = [radio.label for radio in self.app.radio]

        self.assertEqual(len(labels), 3)
        self.assertTrue(any("코사인 유사도" in label for label in labels))
        self.assertTrue(any("난도 지수" in label for label in labels))
        self.assertTrue(any("벡터 축" in label for label in labels))


if __name__ == "__main__":
    unittest.main()
