"""Current distribution metadata must match the root MIT license."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LicenseMetadata(unittest.TestCase):
    def test_current_distribution_metadata(self):
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text())
        files = [ROOT / "SKILL.md", ROOT / "README.md"]
        hub = ROOT / "skills/neon-genie"
        self.assertIn("MIT License", (hub / "LICENSE").read_text())
        self.assertIn("license: MIT", (hub / "SKILL.md").read_text())
        self.assertNotIn(
            "LicenseRef-Zero-State-Proprietary-1.0", (hub / "README.md").read_text()
        )
        files += [
            p
            for p in [
                ROOT / "manifest.json",
                ROOT / "references/manifest.json",
                ROOT / "hyperlex.manifest.yaml",
                ROOT / "pyproject.toml",
            ]
            if p.exists()
        ]
        for p in files:
            with self.subTest(path=str(p)):
                self.assertNotIn("LicenseRef-Zero-State-Proprietary-1.0", p.read_text())
        self.assertIn("license: MIT", (ROOT / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
