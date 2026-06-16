import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TestNewOptimizationSkills(unittest.TestCase):
    def test_continuous_learning_skill_exists(self):
        path = REPO_ROOT / "skills" / "optimization" / "continuous-learning" / "SKILL.md"
        content = path.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("name:", content)
        self.assertIn("description:", content)
        self.assertIn("vex_instinct.py learn", content)

    def test_token_optimization_skill_is_substantial(self):
        path = REPO_ROOT / "skills" / "optimization" / "token-optimization" / "SKILL.md"
        content = path.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        self.assertGreaterEqual(len(content.splitlines()), 150)
        for phrase in ["Prompt slimming", "Model selection", "Context window", "Cost-aware"]:
            self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
