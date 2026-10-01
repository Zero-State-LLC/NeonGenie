#!/usr/bin/env python3
"""Tests for the six 2026-09-30 bake-off changes. Stdlib only. No network."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import judge_eval  # noqa: E402
import packet_compose  # noqa: E402
import research_mode  # noqa: E402

PY = sys.executable
VALIDATE = SCRIPT_DIR / "validate_packet.py"
SAMPLE_V12 = ROOT / "examples" / "packets" / "sample-opportunity-v12.packet.json"
SAMPLE_V13 = ROOT / "examples" / "packets" / "sample-opportunity-v13.packet.json"


def _validate(packet: dict, packet_type: str) -> subprocess.CompletedProcess[str]:
    path = ROOT / "out" / "neon-genie" / "bakeoff-test" / f"{packet_type}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    return subprocess.run(
        [PY, str(VALIDATE), "--packet", str(path), "--type", packet_type],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_offline_skips_adapter_and_observed() -> None:
    class Spy(research_mode.NullAdapter):
        def __init__(self) -> None:
            self.calls = 0

        def gather(self, queries: list[str]) -> list[dict]:
            self.calls += 1
            return [
                {
                    "url": "https://example.test/x",
                    "retrieved_at": "2026-10-01",
                    "text": "Named buyer pays 99",
                    "complete": True,
                }
            ]

    spy = Spy()
    result = research_mode.run_research(
        {"enabled": False, "offline": True},
        ["public price"],
        adapter=spy,
    )
    assert spy.calls == 0
    assert result["observed_claims"] == []
    assert result["research_ran"] is False
    assert result["adapter"] == "null"


def test_observed_requires_url_and_date() -> None:
    items = [
        {
            "url": "https://example.test/paper",
            "retrieved_at": "2026-10-01",
            "complete": True,
            "kind": "paper",
            "text": "The note states no price number is set.",
            "query": "price",
        },
        {
            "retrieved_at": "2026-10-01",
            "complete": True,
            "text": "A body with no URL.",
            "query": "price",
        },
        {
            "url": "https://example.test/partial",
            "complete": False,
            "reason": "body_cap",
            "text": "partial body that must not be labeled",
            "query": "price",
        },
    ]
    result = research_mode.run_research(
        {"enabled": True, "offline": False, "adapter": "fixture"},
        ["price"],
        adapter=research_mode.FixtureAdapter(items),
    )
    assert result["research_ran"] is True
    assert len(result["observed_claims"]) == 1
    claim = result["observed_claims"][0]
    assert claim["label"] == "OBSERVED"
    assert claim["url"].startswith("https://")
    assert claim["retrieved_at"] == "2026-10-01"
    assert claim["kind"] == "paper"
    reasons = {row["reason"] for row in result["rejected"]}
    assert "missing_url" in reasons
    assert "body_cap" in reasons


def test_text_must_come_from_source() -> None:
    claim, reason = research_mode.label_item(
        {
            "url": "https://example.test/src",
            "retrieved_at": "2026-10-01",
            "complete": True,
            "text": "Price is 9",
            "source_text": "No price number is set",
        }
    )
    assert claim is None
    assert reason == "text_not_in_source"


def test_secret_like_body_is_not_observed() -> None:
    body = "see " + "password" + "=example"
    claim, reason = research_mode.label_item(
        {
            "url": "https://example.test/src",
            "retrieved_at": "2026-10-01",
            "complete": True,
            "text": body,
        }
    )
    assert claim is None
    assert reason == "secret_like_body"


def test_http_adapter_uses_opener_and_drops_oversize() -> None:
    class Resp:
        def __init__(self, payload: bytes) -> None:
            self.payload = payload

        def read(self, n: int) -> bytes:
            return self.payload[:n] if n < len(self.payload) else self.payload

        def geturl(self) -> str:
            return "https://example.test/std"

        def __enter__(self) -> "Resp":
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    def opener(req: object, timeout: int = 10) -> Resp:
        assert timeout == 10
        return Resp(b"Public page about a published standard.")

    item = research_mode.fetch_url("https://example.test/std", opener=opener)
    claim, reason = research_mode.label_item(item)
    assert reason is None
    assert claim is not None
    assert claim["label"] == "OBSERVED"
    assert claim["text"] == "Public page about a published standard."

    def huge(req: object, timeout: int = 10) -> Resp:
        return Resp(b"x" * (research_mode.MAX_BODY_BYTES + 5))

    over = research_mode.fetch_url("https://example.test/big", opener=huge)
    assert over["complete"] is False
    assert "text" not in over
    claim, reason = research_mode.label_item(over)
    assert claim is None
    assert reason == "body_cap"

    adapter = research_mode.StdlibHttpAdapter(opener=opener)
    rows = adapter.gather(["not a url", "https://example.test/std"])
    assert rows[0]["reason"] == "not_a_url"
    assert rows[1]["complete"] is True


def test_input_contradictions_from_fixture_notes() -> None:
    scanned = packet_compose.scan_input_notes(packet_compose.SEAT_OPTION_NOTES)
    assert scanned["checked"] is True
    kinds = {row["kind"] for row in scanned["findings"]}
    assert kinds == {"contradiction", "arithmetic_error", "inconsistent_figure"}
    blob = json.dumps(scanned).lower()
    assert "acme" not in blob
    assert "buyer" not in blob
    assert "revenue" not in blob
    clean = packet_compose.scan_input_notes("The operator has not declared a buyer.")
    assert clean["findings"] == []
    assert packet_compose.scan_input_notes("10 × 5 = 50.")["findings"] == []
    rent = packet_compose.scan_input_notes(
        "Asking rent is $5.50/sf/mo. Phase 4 uses a $60/sf/yr band."
    )
    assert any(row["kind"] == "inconsistent_figure" for row in rent["findings"])


def test_prose_kill_and_structured_kill() -> None:
    prose = {"schema_version": "1.2.0", "kill_criteria": "Stop if nobody buys."}
    errors = packet_compose.packaging_errors(prose, "opportunity")
    assert any(line.startswith("NG-KILL-001") for line in errors)
    structured = {
        "schema_version": "1.1.0",
        "kill_criteria": [
            {
                "metric": "paid_yes_count",
                "threshold": 1,
                "comparison": "lt",
                "check_date": "2026-10-15",
                "data_source": "operator ledger",
                "claim_label": "OBSERVED",
            }
        ],
    }
    errors = packet_compose.packaging_errors(structured, "commercial")
    assert any(line.startswith("NG-KILL-003") for line in errors)
    legacy = {
        "blocked_transition": {"from": "a", "to": "b"},
        "outcome_model": {},
        "system_topology": {},
        "opportunity_thesis": "legacy",
        "validation_path": [],
        "completion_proof": "proof",
        "scorecard": {},
        "promotion_state": "CONCEPTUAL",
        "logic_label": "mixed",
    }
    assert packet_compose.packaging_errors(legacy, "opportunity") == []


def test_first_commit_required_on_v12() -> None:
    packet = {
        "schema_version": "1.2.0",
        "build_handoff": {"summary": "steps only"},
    }
    errors = packet_compose.packaging_errors(packet, "opportunity")
    assert any(line.startswith("NG-HANDOFF-001") for line in errors)


def test_page_budget_moves_evidence_without_truncation() -> None:
    long = ("alpha " * 800).strip()
    assert len(long.split()) > packet_compose.WORD_BUDGET
    packet = packet_compose.attach_v12(
        {
            "opportunity_thesis": "Short thesis.",
            "completion_proof": "A revised note.",
        },
        notes="10 × 5 = 100.",
        research_policy={"enabled": True, "offline": False, "adapter": "fixture"},
        queries=["alpha"],
        schema_id="neon-genie/opportunity-packet",
        adapter=research_mode.FixtureAdapter(
            [
                {
                    "url": "https://example.test/long",
                    "retrieved_at": "2026-10-01",
                    "complete": True,
                    "kind": "web_page",
                    "text": long,
                    "query": "alpha",
                }
            ]
        ),
        handoff={
            "summary": "Read the appendix.",
            "first_commit": {
                "touch": ["notes"],
                "done_when": "The long page is still complete in the appendix.",
                "test_to_write": "Assert the appendix text equals the source text.",
                "owner_role": "operator",
            },
        },
        kill_criteria=[
            {
                "criterion_id": "kc-1",
                "metric": "open_findings",
                "threshold": 0,
                "comparison": "gt",
                "check_date": "2026-10-15",
                "data_source": "input contradiction pass",
                "claim_label": "SPECULATIVE",
                "derivation": packet_compose.identity_derivation(0),
            }
        ],
    )
    assert packet["page_budget"]["truncated"] is False
    assert packet["page_budget"]["fits_one_page"] is True
    appendix_text = packet["appendix"]["research_claims"][0]["text"]
    assert appendix_text == long
    main_claim = packet["research"]["observed_claims"][0]
    assert "text" not in main_claim
    assert long not in packet_compose.prose_main(packet)
    evidence = packet["appendix"]["contradiction_evidence"][0]["evidence"]
    assert evidence == "10 × 5 = 100"

    huge = dict(packet)
    huge["opportunity_thesis"] = "word " * 500
    huge = packet_compose.apply_page_budget(huge)
    assert huge["opportunity_thesis"] == "word " * 500
    assert huge["page_budget"]["truncated"] is False
    assert huge["page_budget"]["fits_one_page"] is False
    errors = packet_compose.packaging_errors(huge, "opportunity")
    assert any(line.startswith("NG-PAGE-001") for line in errors)


def test_sample_v12_and_legacy_samples() -> None:
    legacy_v12 = json.loads(SAMPLE_V12.read_text(encoding="utf-8"))
    assert legacy_v12["schema_version"] == "1.2.0"
    packet = packet_compose.seat_option_example_packet()
    assert packet["schema_version"] == "1.3.0"
    on_disk = json.loads(SAMPLE_V13.read_text(encoding="utf-8"))
    assert on_disk == packet
    result = _validate(packet, "opportunity")
    assert result.returncode == 0, result.stderr
    blob = json.dumps(packet)
    assert "NOT_COMPUTABLE_until_declared" in blob
    assert "https://example.test/fixtures/seat-floor" in blob
    assert packet["research"]["observed_claims"][0]["label"] == "OBSERVED"
    assert packet["build_handoff"]["first_commit"]["owner_role"] == "operator"
    assert packet["page_budget"]["fits_one_page"] is True
    assert packet["page_budget"]["truncated"] is False
    for legacy, kind in (
        ("examples/packets/sample-opportunity.packet.json", "opportunity"),
        ("examples/packets/sample-commercial.packet.json", "commercial"),
    ):
        proc = subprocess.run(
            [PY, str(VALIDATE), "--packet", str(ROOT / legacy), "--type", kind],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr


def test_dual_judges_are_blind_and_swapped() -> None:
    packets = [
        {
            "id": "left-arm",
            "body": "Neon Genie says the buyer is NOT_COMPUTABLE and no price is set.",
        },
        {
            "id": "right-arm",
            "body": "Opus baseline offers an illustrative hosted tier.",
        },
    ]
    scores_one = {name: 1.5 for name in judge_eval.ALL_CRITERIA}
    scores_two = {name: 1.1 for name in judge_eval.ALL_CRITERIA}
    winner = {name: 1.8 for name in judge_eval.ALL_CRITERIA}
    judges = [
        judge_eval.load_judge(
            {
                "kind": "fixture",
                "name": "judge-one",
                "winner_excerpt": "NOT_COMPUTABLE",
                "rows": [{"excerpt": "NOT_COMPUTABLE", **winner}],
                "default_scores": scores_one,
            }
        ),
        judge_eval.load_judge(
            {
                "kind": "fixture",
                "name": "judge-two",
                "winner_excerpt": "NOT_COMPUTABLE",
                "rows": [{"excerpt": "NOT_COMPUTABLE", **{k: 1.4 for k in winner}}],
                "default_scores": scores_two,
            }
        ),
    ]
    seen: list[str] = []
    original_score = judges[0].score

    def wrapped(document: str, criteria: tuple[str, ...]) -> dict[str, float]:
        seen.append(document)
        assert "neon" not in document.lower()
        assert "opus" not in document.lower()
        return original_score(document, criteria)

    judges[0].score = wrapped  # type: ignore[method-assign]
    result = judge_eval.run_panel(packets, judges, seed=20260930)
    assert result["model_invoked"] is False
    assert result["judge_count"] == 2
    for criterion in judge_eval.NEUTRAL_CRITERIA:
        assert criterion in result["criteria"]
    assert seen
    assert result["pairwise"]
    assert judge_eval.agreed_source(result) == "left-arm"
    by_judge: dict[str, float] = {}
    for row in result["scores"]:
        by_judge.setdefault(row["judge"], row["scores"]["founder_usefulness"])
    assert by_judge["judge-one"] != by_judge["judge-two"]
    try:
        judge_eval.load_judge({"kind": "paid"})
        raise AssertionError("paid judge should be rejected")
    except judge_eval.JudgeRejected as exc:
        assert "NG-JUDGE-001" in str(exc)
    source = (SCRIPT_DIR / "judge_eval.py").read_text(encoding="utf-8")
    assert "urlopen" not in source
    assert "api_key" not in source


def test_v12_sample_has_no_secret_markers() -> None:
    text = SAMPLE_V12.read_text(encoding="utf-8")
    assert "PRIVATE KEY" not in text
    assert "Bearer " not in text
    assert "sk-" not in text


def main() -> int:
    tests = [
        test_offline_skips_adapter_and_observed,
        test_observed_requires_url_and_date,
        test_text_must_come_from_source,
        test_secret_like_body_is_not_observed,
        test_http_adapter_uses_opener_and_drops_oversize,
        test_input_contradictions_from_fixture_notes,
        test_prose_kill_and_structured_kill,
        test_first_commit_required_on_v12,
        test_page_budget_moves_evidence_without_truncation,
        test_sample_v12_and_legacy_samples,
        test_dual_judges_are_blind_and_swapped,
        test_v12_sample_has_no_secret_markers,
    ]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print("PASS: bake-off six packaging checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
