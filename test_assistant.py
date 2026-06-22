import unittest

from assistant import answer_question


class AssistantTests(unittest.TestCase):
    def test_crop_answer(self):
        self.assertIn("Rice", answer_question("Tell me about rice"))

    def test_crop_alias(self):
        self.assertIn("Kidney Beans", answer_question("How should I grow rajma?"))

    def test_soil_answer(self):
        self.assertIn("cotton", answer_question("What grows in black soil?"))

    def test_unknown_answer_is_honest(self):
        self.assertIn("do not have", answer_question("Explain tractor finance"))


if __name__ == "__main__":
    unittest.main()
