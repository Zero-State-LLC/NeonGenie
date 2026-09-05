"""Runtime installs must not depend on repository CI files."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuntimeLayout(unittest.TestCase):
    def test_runtime_without_github(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", ".github", "skills", "__pycache__", "out"
                ),
            )
            result = subprocess.run(
                check=False,
                args=[sys.executable, str(root / "scripts/validate_hermes_skill.py")],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_requires_executable_skill_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(
                ROOT,
                root,
                ignore=shutil.ignore_patterns(
                    ".git", ".github", "skills", "__pycache__", "out"
                ),
            )
            result = subprocess.run(
                check=False,
                args=[
                    sys.executable,
                    str(root / "scripts/validate_hermes_skill.py"),
                    "--repository",
                ],
                cwd=tmp,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
        workflow = (ROOT / ".github/workflows/hermes-evals.yml").read_text()
        for command in (
            "do check",
            "do eval",
            "do doctor",
            "do runtime",
            "distribution_spine.py verify",
        ):
            self.assertIn(command, workflow)


if __name__ == "__main__":
    unittest.main()
