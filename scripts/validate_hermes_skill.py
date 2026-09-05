#!/usr/bin/env python3
"""Validate Neon Genie as a portable, self-contained Hermes skill.

Uses only the Python standard library. Run from any working directory:
    python scripts/validate_hermes_skill.py

Supports full tree (schemas/, profiles/, evals/) and Hermes hub layout
(references/schemas/, references/profiles/, examples/evals/).
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import paths as ng_paths  # noqa: E402

SKILL_FILE = SKILL_ROOT / "SKILL.md"

# Hermes Agent v0.21 hardline (tools/skill_linter.py + skill-authoring SKILL.md).
# Index truncates at SKILL_PROMPT_DESC_LIMIT (57 chars + "...").
SKILL_PROMPT_DESC_LIMIT = 60
REQUIRED_FRONTMATTER = {
    "name",
    "description",
    "version",
    "author",
    "license",
    "platforms",
}
REQUIRED_HERMES_KEYS = {"tags", "related_skills"}
MARKETING_WORDS = (
    "powerful",
    "comprehensive",
    "seamless",
    "advanced",
    "cutting-edge",
    "state-of-the-art",
    "revolutionary",
    "robust",
)

# Paths that must exist either at full-tree location or hub mirror.
# Each entry is a list of candidate relative paths (first existing wins).
REQUIRED_ANY: list[list[str]] = [
    ["SKILL.md"],
    ["manifest.json", "references/manifest.json"],
    ["VERSION", "references/VERSION"],
    ["references/hermes-runtime-contract.md"],
    ["references/CAPABILITY_MAP.md"],
    ["references/GOLDEN_TESTS.md"],
    ["references/anti-overclaim-patterns.md"],
    ["references/post-seal-verification.md"],
    ["profiles", "references/profiles"],
    ["schemas", "references/schemas"],
    ["schemas/data-request.schema.json", "references/schemas/data-request.schema.json"],
    [
        "schemas/learning-ledger-entry.schema.json",
        "references/schemas/learning-ledger-entry.schema.json",
    ],
    ["templates/request.yaml"],
    ["evals", "examples/evals"],
    ["evals/rubric.md", "examples/evals/rubric.md"],
    ["examples/README.md"],
    ["scripts/paths.py"],
    ["scripts/distribution_spine.py"],
    ["scripts/check_behavioral_invariants.py"],
    ["scripts/hermes_runtime_smoke.py"],
    ["scripts/lineage.py"],
    ["scripts/build_envelope.py"],
    ["scripts/run_job.py"],
    ["scripts/capabilities.py"],
    ["scripts/reconcile_learning.py"],
    ["scripts/release_check.py"],
    ["scripts/validate_hermes_skill.py"],
    ["scripts/neon_genie.py"],
    ["scripts/validate_packet.py"],
    ["scripts/route_profiles.py"],
    ["scripts/build_receipt.py"],
    ["scripts/run_fixture_invariants.py"],
    ["scripts/audit_release_version.py"],
    ["scripts/run_hermes_evals.py"],
    ["scripts/check_transcripts.py"],
    ["scripts/record_learning.py"],
    ["scripts/recipe_run.py"],
    ["scripts/recipe_common.py"],
    ["scripts/recipe_product_audit.py"],
    ["scripts/doctor.py"],
    ["examples/fragmentation.brief.yaml"],
    ["examples/zero-option-with-skills.brief.yaml"],
    ["examples/packets/sample-opportunity.packet.json"],
    ["evals/transcripts/README.md", "examples/evals/transcripts/README.md"],
    ["evals/transcripts/rubric.md", "examples/evals/transcripts/rubric.md"],
    ["examples/commercial.brief.yaml"],
    ["examples/audit.brief.yaml"],
    ["examples/agentic.brief.yaml"],
    ["examples/memetic.brief.yaml"],
    ["examples/evidence.brief.yaml"],
    ["examples/opportunity.brief.yaml"],
    [
        "evals/transcripts/06-agentic-x402-misfit.md",
        "examples/evals/transcripts/06-agentic-x402-misfit.md",
    ],
    [
        "evals/transcripts/07-memetic-cannot-promote.md",
        "examples/evals/transcripts/07-memetic-cannot-promote.md",
    ],
    [
        "evals/transcripts/08-evidence-intelligence.md",
        "examples/evals/transcripts/08-evidence-intelligence.md",
    ],
    [
        "evals/transcripts/09-opportunity-mining.md",
        "examples/evals/transcripts/09-opportunity-mining.md",
    ],
]

# Full-tree only (skipped on hub layout)
FULL_ONLY: list[str] = [
    "QUICKSTART.md",
    "docs/PREMIERE.md",
    "docs/DEMO.md",
    "install.sh",
    "examples/gallery/README.md",
    "distribution.yaml",
]

FORBIDDEN_PATTERNS = [
    re.compile(r"pip install -e"),
    re.compile(r"/Users/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
]


def _strip_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _fold_block(lines: list[str], start: int, indent: int, literal: bool) -> tuple[str, int]:
    collected: list[str] = []
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            collected.append("")
            i += 1
            continue
        leading = len(line) - len(line.lstrip(" "))
        if leading < indent:
            break
        collected.append(line[indent:] if leading >= indent else line.lstrip())
        i += 1
    while collected and collected[-1] == "":
        collected.pop()
    if literal:
        return "\n".join(collected), i
    paragraphs = "\n".join(collected).split("\n\n")
    folded = " ".join(" ".join(p.split()) for p in paragraphs if p.strip())
    return folded, i


def parse_frontmatter(text: str) -> dict[str, object]:
    """Parse SKILL.md YAML frontmatter. Frontmatter must start at byte 0."""
    if text.startswith("\ufeff"):
        raise ValueError("SKILL.md frontmatter must start at byte 0 (BOM present)")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    fields: dict[str, object] = {}
    lines = text[4:end].splitlines()
    i = 0
    hermes: dict[str, object] = {}
    in_hermes = False
    hermes_indent = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if in_hermes and indent <= hermes_indent:
            in_hermes = False
        if in_hermes and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            val = value.strip()
            if val in {">", "|", ">-", "|-", ">+", "|+"}:
                block, i = _fold_block(
                    lines, i + 1, indent + 2, literal=val.startswith("|")
                )
                hermes[key] = block
                continue
            hermes[key] = _strip_yaml_scalar(val) if val else []
            i += 1
            continue
        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            val = value.strip()
            if val in {">", "|", ">-", "|-", ">+", "|+"}:
                block, i = _fold_block(
                    lines, i + 1, 2, literal=val.startswith("|")
                )
                fields[key] = block
                continue
            fields[key] = _strip_yaml_scalar(val)
            i += 1
            continue
        if stripped == "hermes:" or stripped.startswith("hermes:"):
            in_hermes = True
            hermes_indent = indent
            i += 1
            continue
        i += 1
    if hermes:
        fields["_hermes"] = hermes
    return fields


def validate_description(description: str) -> list[str]:
    errors: list[str] = []
    desc = str(description or "").strip()
    if not desc:
        errors.append("Frontmatter description is empty")
        return errors
    if len(desc) > SKILL_PROMPT_DESC_LIMIT:
        errors.append(
            f"Frontmatter description is {len(desc)} chars; Hermes index "
            f"truncates past {SKILL_PROMPT_DESC_LIMIT} (57 + '...'). "
            "Keep one sentence that ends with a period."
        )
    if not desc.endswith("."):
        errors.append("Frontmatter description must end with a period")
    if desc.count(".") > 1:
        errors.append("Frontmatter description must be one sentence")
    lower = desc.lower()
    hits = [w for w in MARKETING_WORDS if re.search(rf"\b{re.escape(w)}\b", lower)]
    if hits:
        errors.append(f"Frontmatter description contains marketing words: {hits}")
    return errors


def referenced_relative_paths(text: str) -> set[str]:
    candidates: set[str] = set()
    for match in re.finditer(
        r"`((?:profiles|schemas|references|scripts|evals|templates|examples)/[^`\n]+)`",
        text,
    ):
        value = match.group(1)
        if " " not in value and not value.startswith("/"):
            candidates.add(value.rstrip(".,;:"))
    return candidates


def resolve_any(candidates: list[str]) -> Path | None:
    for rel in candidates:
        path = SKILL_ROOT / rel
        if path.exists():
            return path
    return None


def validate_python(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        errors.append(f"Python compile failure: {path.relative_to(SKILL_ROOT)}: {exc}")
    return errors


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if any(a in {"-h", "--help"} for a in argv):
        print("Validate Neon Genie as a portable Hermes skill (stdlib only).")
        print("Usage: python scripts/validate_hermes_skill.py [--repository]")
        print("Exit 0 on PASS; non-zero on FAIL with reasons on stderr.")
        return 0

    if any(a != "--repository" for a in argv):
        print("Unknown option; use --repository for CI validation", file=sys.stderr)
        return 2
    errors: list[str] = []
    if "--repository" in argv:
        workflow = SKILL_ROOT / ".github/workflows/hermes-evals.yml"
        if not workflow.is_file():
            errors.append("Repository CI workflow missing: .github/workflows/hermes-evals.yml")
    hub = ng_paths.is_hub_layout()

    if not SKILL_FILE.is_file():
        print("FAIL: SKILL.md missing", file=sys.stderr)
        return 1

    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    try:
        frontmatter = parse_frontmatter(skill_text)
    except ValueError as exc:
        errors.append(str(exc))
        frontmatter = {}

    missing_fields = sorted(REQUIRED_FRONTMATTER - set(frontmatter))
    if missing_fields:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_fields)}")
    if frontmatter.get("name") != "neon-genie":
        errors.append("Frontmatter name must be 'neon-genie'")
    errors.extend(validate_description(str(frontmatter.get("description", ""))))
    hermes_meta = frontmatter.get("_hermes")
    if not isinstance(hermes_meta, dict):
        errors.append("Missing frontmatter metadata.hermes.{tags, related_skills}")
    else:
        missing_hermes = sorted(REQUIRED_HERMES_KEYS - set(hermes_meta))
        if missing_hermes:
            errors.append(
                "Missing metadata.hermes fields: " + ", ".join(missing_hermes)
            )

    version_fm = str(frontmatter.get("version", ""))
    try:
        version_file = ng_paths.version_path().read_text(encoding="utf-8").strip()
    except (OSError, FileNotFoundError):
        errors.append("VERSION missing (also tried references/VERSION)")
        version_file = ""

    manifest: dict = {}
    try:
        manifest = json.loads(ng_paths.manifest_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append("manifest.json missing (also tried references/manifest.json)")
    except json.JSONDecodeError as exc:
        errors.append(f"manifest.json invalid JSON: {exc}")

    version_manifest = str(manifest.get("version", ""))
    if version_file and version_fm and version_file != version_fm:
        errors.append(
            f"VERSION ({version_file}) != SKILL frontmatter version ({version_fm})"
        )
    if version_file and version_manifest and version_file != version_manifest:
        errors.append(
            f"VERSION ({version_file}) != manifest.json version ({version_manifest})"
        )
    if version_fm and version_manifest and version_fm != version_manifest:
        errors.append(
            f"SKILL frontmatter version ({version_fm}) != manifest.json version ({version_manifest})"
        )

    for candidates in REQUIRED_ANY:
        if resolve_any(candidates) is None:
            errors.append(f"Missing required path (any of): {', '.join(candidates)}")

    if not hub:
        for relative in FULL_ONLY:
            if not (SKILL_ROOT / relative).exists():
                errors.append(f"Missing required path: {relative}")

    profiles = manifest.get("profiles") or []
    if not isinstance(profiles, list) or not profiles:
        errors.append("manifest.json profiles must be a non-empty list")
    else:
        try:
            pdir = ng_paths.profiles_dir()
        except FileNotFoundError:
            pdir = None
            errors.append("profiles/ missing (also tried references/profiles/)")
        if pdir is not None:
            for name in profiles:
                p = pdir / f"{name}.md"
                if not p.is_file():
                    errors.append(f"Profile listed in manifest but missing: {name}.md")

    # Hub-allowlisted references in SKILL.md must exist when listed as concrete files
    for rel in sorted(referenced_relative_paths(skill_text)):
        target = SKILL_ROOT / rel
        if target.exists():
            continue
        # Dual-path fallbacks for historical root paths
        alts = []
        if rel.startswith("schemas/"):
            alts.append(SKILL_ROOT / "references" / rel)
        elif rel.startswith("profiles/"):
            alts.append(SKILL_ROOT / "references" / rel)
        elif rel.startswith("evals/"):
            alts.append(SKILL_ROOT / "examples" / rel)
        if any(a.exists() for a in alts):
            continue
        # Directory-style refs like profiles/ are ok if dual-path dir exists
        if rel.rstrip("/").endswith(("profiles", "schemas", "evals")):
            continue
        errors.append(f"SKILL.md references missing path: {rel}")

    scripts_dir = SKILL_ROOT / "scripts"
    if scripts_dir.is_dir():
        for py in sorted(scripts_dir.glob("*.py")):
            errors.extend(validate_python(py))

    for rel in (
        "SKILL.md",
        "QUICKSTART.md",
        "references/hermes-runtime-contract.md",
        "README.md",
    ):
        path = SKILL_ROOT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pat in FORBIDDEN_PATTERNS:
            if pat.search(text):
                errors.append(f"Forbidden pattern {pat.pattern!r} in {rel}")

    if errors:
        print("FAIL: Neon Genie skill validation", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("PASS: Neon Genie skill validation")
    print(f"  root: {SKILL_ROOT}")
    print(f"  layout: {'hub' if hub else 'full'}")
    print(f"  version: {version_file or version_fm or version_manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
