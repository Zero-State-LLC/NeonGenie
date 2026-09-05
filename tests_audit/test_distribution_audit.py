import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "distribution", ROOT / "scripts/distribution_spine.py"
)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DistributionAudit(unittest.TestCase):
    def test_optional_routes_are_linked_and_safety_retained(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("references/profile-routing.md", text)
        self.assertIn("references/output-selection.md", text)
        self.assertNotIn("profile_router:", text)
        self.assertIn(
            "profile_router:", (ROOT / "references/profile-routing.md").read_text()
        )
        for required in [
            "12. **Mandatory gates.**",
            "Gate Y",
            "Gate P",
            "still stay advisory only",
            "PROPOSED",
            "## Verification",
            "PRIVACY_EGRESS_CHECK",
        ]:
            self.assertIn(required, text)

    def test_package_sync_preserves_license_and_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            shutil.copytree(
                ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", "out")
            )
            package = root / "skills/neon-genie"
            originals = {
                p.relative_to(package): p.read_bytes()
                for p in package.rglob("*")
                if p.is_file() and (p.name == "LICENSE" or ".github" in p.parts)
            }
            dist = m.load_distribution(root)
            m.sync_hub_package(root, dist)
            for rel, content in originals.items():
                self.assertEqual((package / rel).read_bytes(), content, str(rel))
            self.assertIn("license: MIT", (package / "SKILL.md").read_text())
            for rel in ["AGENTS.md", "CLAUDE.md", "intent"]:
                self.assertFalse((package / rel).exists())
            self.assertEqual(m.verify_package_parity(root, dist), [])


if __name__ == "__main__":
    unittest.main()
