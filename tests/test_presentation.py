"""문제 원문·통계·원리 퀴즈에 대한 표시 규칙."""

import unittest

import analysis as A
import presentation as P


class QuestionMaterialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.exam = A.load()

    def test_question_uses_its_full_passage_and_related_box(self) -> None:
        material = P.question_material(self.exam, 4)

        self.assertEqual(material["passage"], self.exam["passages"]["1-5"])
        self.assertEqual(material["box"], self.exam["boxes"]["4-5"])
        self.assertEqual(material["stem"], self.exam["questions"][3]["stem"])

    def test_question_without_box_does_not_borrow_another_box(self) -> None:
        material = P.question_material(self.exam, 3)

        self.assertIsNone(material["box"])

    def test_unknown_question_is_rejected_clearly(self) -> None:
        with self.assertRaisesRegex(ValueError, "존재하지 않는 문항"):
            P.question_material(self.exam, 99)

    def test_literature_question_uses_second_passage_and_box(self) -> None:
        material = P.question_material(self.exam, 10)

        self.assertEqual(material["passage"], self.exam["passages"]["6-10"])
        self.assertEqual(material["box"], self.exam["boxes"]["9-10"])

    def test_option_statistics_keep_every_option_text_and_answer_state(self) -> None:
        question = self.exam["questions"][4]
        rows = P.option_stat_rows(question)

        self.assertEqual([row["선지 내용"] for row in rows], [option["text"] for option in question["options"]])
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[1]["표시"], "정답")
        self.assertEqual(rows[2]["표시"], "내 답")
        self.assertEqual(rows[1]["정답과 cos"], 1.0)


class PrincipleQuizTest(unittest.TestCase):
    def test_quiz_asks_model_principles_not_question_parts(self) -> None:
        quiz = P.principle_quiz()

        self.assertEqual({item["concept"] for item in quiz}, {"코사인 유사도", "난도 지수", "벡터 축"})
        self.assertTrue(all("번" not in item["question"] for item in quiz))
        self.assertTrue(all(item["answer"] in item["choices"] for item in quiz))


class SolveQuestionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.question = A.load()["questions"][0]

    def test_missing_answer_asks_for_a_choice(self) -> None:
        feedback = P.answer_feedback(self.question, None)

        self.assertEqual(feedback["kind"], "warning")
        self.assertNotIn("⑤", feedback["message"])

    def test_correct_answer_is_confirmed(self) -> None:
        feedback = P.answer_feedback(self.question, 5)

        self.assertEqual(feedback, {"kind": "success", "message": "정답입니다. 정답은 ⑤입니다."})

    def test_wrong_answer_reveals_the_correct_choice(self) -> None:
        feedback = P.answer_feedback(self.question, 1)

        self.assertEqual(feedback, {"kind": "error", "message": "오답입니다. 정답은 ⑤입니다."})

    def test_glossary_defines_the_model_terms(self) -> None:
        terms = {item["용어"] for item in P.glossary()}

        self.assertEqual(
            terms,
            {"선지", "벡터", "근거 지지도", "단어 효과", "코사인 유사도", "문턱 τ", "난도 지수 D"},
        )

    def test_example_dataset_keeps_answer_and_my_answer_separate(self) -> None:
        question = A.load()["questions"][4]
        rows = P.example_dataset_rows(question)

        self.assertEqual(rows[1]["정답"], "✓")
        self.assertEqual(rows[1]["내 답"], "")
        self.assertEqual(rows[2]["정답"], "")
        self.assertEqual(rows[2]["내 답"], "✓")
        self.assertEqual(rows[2]["선지 내용"], question["options"][2]["text"])


if __name__ == "__main__":
    unittest.main()
