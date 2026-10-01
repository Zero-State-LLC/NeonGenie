#!/usr/bin/env python3
"""Round-2 bake-off checks. Stdlib only. No network and no paid calls.

The round-2 report says a host review found 14 input issues and does not
list them. These fixtures are the defects that report, and the round-1
report, actually name, plus the arithmetic classes the follow-up asked for.
v3.30 dropped phrase rules fitted to packet wording. The count, quantity,
period, and included-at cases below are the general forms of those checks.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import judge_eval
import packet_compose
import research_mode

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
VALIDATE = ROOT / "scripts" / "validate_packet.py"
SAMPLE_V12 = ROOT / "examples" / "packets" / "sample-opportunity-v12.packet.json"

# Named in the round-1 or round-2 writeup, or the arithmetic the follow-up
# asked the scanner to perform. Not a reconstruction of an unpublished list.
RECONSTRUCTED = [
    (
        "hyperlex-status",
        "The gap packet still says 1.2B weekly users is UNVERIFIED (the CARD verified it).",
        "contradiction",
        "UNVERIFIED and verified",
    ),
    (
        "count-clash",
        "The pitch says one build serves all three. The hackathon Token Factory runtime rule is one runtime, not three products.",
        "contradiction",
        "serves all three",
    ),
    (
        "labeled-quantity",
        "seat count: 2\nseat count: 1",
        "inconsistent_figure",
        "seat count",
    ),
    (
        "monthly-yearly",
        "The fee is $10 monthly. The fee is $100 yearly.",
        "inconsistent_figure",
        "yearly",
    ),
    (
        "included-at-n",
        "The per-tenant floor includes an operator seat at N=1 but not at N=10 or N=50.",
        "inconsistent_figure",
        "omitted at N",
    ),
    (
        "autogive-seats-times-price",
        "Heavy floor: 2 seats × $318 = $700.",
        "arithmetic_error",
        "700",
    ),
    (
        "autogive-fee-total",
        "subtotal $100, Stripe fee $3.20, fee-inclusive total $100.",
        "arithmetic_error",
        "100 + 3.2",
    ),
    (
        "autogive-fee-percent",
        "$200 plus a 2.9% fee and $0.30 equals $200.",
        "arithmetic_error",
        "206.1",
    ),
    (
        "autogive-per-unit",
        "The per-unit floor is flat.\nN=1 per-unit floor $636.\nN=10 per-unit floor $318.",
        "inconsistent_figure",
        "per-unit",
    ),
    (
        "autogive-per-seat",
        "Use the same per-seat rate.\nN=1 per-seat $318.\nN=10 per-seat $300.",
        "inconsistent_figure",
        "per-seat",
    ),
    (
        "autogive-token-floor",
        "token floor: $170\ntoken floor: $650",
        "inconsistent_figure",
        "token floor",
    ),
    (
        "alta-rent",
        "Asking rent is $5.50/sf/mo. The Phase 4 band is $60 per sf per year.",
        "inconsistent_figure",
        "66",
    ),
    (
        "alta-rationale",
        "\n".join(
            [
                "Option A: the operator keeps the leftover inventory.",
                "Option B: the buyer takes the leftover inventory.",
                "Rationale for Option A: the buyer takes the leftover inventory.",
            ]
        ),
        "contradiction",
        "describes Option B",
    ),
]


def test_reconstructed_note_defects() -> None:
    assert len(RECONSTRUCTED) == 13
    for name, notes, kind, snippet in RECONSTRUCTED:
        scanned = packet_compose.scan_input_notes(notes)
        matches = [
            row
            for row in scanned["findings"]
            if row["kind"] == kind and snippet in row["summary"]
        ]
        assert matches, (name, scanned["findings"])
        assert all(row["claim_label"] == "OBSERVED" for row in matches)


def test_magnitude_suffix_is_not_stripped() -> None:
    same = packet_compose.scan_input_notes(
        "price floor: $300k\nprice floor: $300,000"
    )
    assert same["findings"] == []
    different = packet_compose.scan_input_notes(
        "price floor: $300k\nprice floor: $300"
    )
    assert any(row["kind"] == "inconsistent_figure" for row in different["findings"])
    assert "300" in different["findings"][0]["summary"] or different["findings"]


def test_kill_recompute_includes_fee_and_every_tier() -> None:
    wrong = {
        "schema_version": "1.3.0",
        "kill_criteria": [
            {
                "metric": "token_net_of_stripe",
                "threshold": 170,
                "comparison": "lt",
                "check_date": "2026-10-15",
                "data_source": "operator tier table",
                "claim_label": "INFERRED",
                "derivation": {
                    "formula": "min_tier_net_of_fee",
                    "inputs": {
                        "tiers": [170, 650],
                        "percent": 0.029,
                        "fixed": 0.30,
                        "tier_count": 2,
                    },
                    "depends_on": ["every_tier", "stripe_percent", "stripe_fixed"],
                },
            }
        ],
    }
    errors = packet_compose.packaging_errors(wrong, "opportunity")
    assert any(line.startswith("NG-KILL-004") for line in errors)
    missing = {
        "schema_version": "1.3.0",
        "kill_criteria": [
            {
                "metric": "token_net_of_stripe",
                "threshold": 170,
                "comparison": "lt",
                "check_date": "2026-10-15",
                "data_source": "operator tier table",
                "claim_label": "INFERRED",
                "derivation": {
                    "formula": "min_tier_net_of_fee",
                    "inputs": {"tiers": [170], "tier_count": 2},
                    "depends_on": ["every_tier", "stripe_percent", "stripe_fixed"],
                },
            }
        ],
    }
    missing_errors = packet_compose.packaging_errors(missing, "opportunity")
    assert any(line.startswith("NG-KILL-005") for line in missing_errors)
    net = min(170, 650) * (1 - 0.029) - 0.30
    corrected = json.loads(json.dumps(wrong))
    corrected["kill_criteria"][0]["threshold"] = net
    # Other 1.3 sections are still absent; the recompute itself must be clean.
    recompute_errors = [
        line
        for line in packet_compose.packaging_errors(corrected, "opportunity")
        if line.startswith("NG-KILL-004") or line.startswith("NG-KILL-005")
    ]
    assert recompute_errors == []


class _QuoteJudge:
    def __init__(self, verdict: str) -> None:
        self.verdict = verdict
        self.calls = 0

    def assess(self, claim: str, quote: str) -> str:
        self.calls += 1
        return self.verdict


def _observed_claim(text: str, quote: str, retrieved: str = "2026-10-01") -> dict:
    return {
        "schema_version": "1.1.0",
        "claims": [
            {
                "label": "OBSERVED",
                "text": text,
                "quote": quote,
                "retrieved_at": retrieved,
            }
        ],
    }


def test_placeholder_date_and_quote_support() -> None:
    dated = {
        "schema_version": "1.3.0",
        "kill_criteria": [
            {
                "metric": "named_lois",
                "threshold": 3,
                "comparison": "lt",
                "check_date": "1970-01-01",
                "data_source": "operator log",
                "claim_label": "OBSERVED",
                "evidence_refs": ["operator_log"],
                "derivation": packet_compose.identity_derivation(3),
            }
        ],
    }
    assert any(
        line.startswith("NG-LABEL-001")
        for line in packet_compose.packaging_errors(dated, "opportunity")
    )
    polarity = _observed_claim(
        "The notes record 3 negative test cases.",
        "The notes record 3 positive test cases that passed.",
    )
    assert any(
        line.startswith("NG-LABEL-002")
        for line in packet_compose.packaging_errors(polarity, "opportunity")
    )
    inconclusive = _observed_claim(
        "The page describes the checkout flow.",
        "See the linked document for context.",
    )
    assert any(
        line.startswith("NG-LABEL-003")
        for line in packet_compose.packaging_errors(inconclusive, "opportunity")
    )
    judge = _QuoteJudge("supports")
    judged = packet_compose.packaging_errors(inconclusive, "opportunity", quote_judge=judge)
    assert judge.calls == 1
    assert not any(line.startswith("NG-LABEL-") for line in judged)
    # A deterministic contradiction is not overruled.
    overruled = _QuoteJudge("supports")
    still = packet_compose.packaging_errors(polarity, "opportunity", quote_judge=overruled)
    assert any(line.startswith("NG-LABEL-002") for line in still)
    assert overruled.calls == 0


class _Resp:
    def __init__(self, body: bytes, url: str, status: int = 200) -> None:
        self._body = body
        self._url = url
        self.status = status

    def read(self, _n: int = -1) -> bytes:
        return self._body

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> _Resp:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def test_robots_fetch_is_free_and_fail_closed() -> None:
    calls: list[str] = []

    def opener(req: object, timeout: int = 10) -> _Resp:
        assert timeout == 10
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        calls.append(url)
        if url.endswith("/robots.txt"):
            body = b"User-agent: *\nDisallow: /private\nAllow: /public\n"
            return _Resp(body, url)
        return _Resp(b"Public fixture page.", url)

    adapter = research_mode.RobotsHttpAdapter(opener=opener)
    blocked = adapter.gather(["https://example.test/private/note"])
    assert blocked[0]["reason"] == "robots_disallow"
    assert blocked[0]["complete"] is False
    assert not any(url.endswith("/private/note") for url in calls)
    allowed = adapter.gather(["https://example.test/public/note"])
    assert allowed[0]["complete"] is True
    assert allowed[0]["text"] == "Public fixture page."
    paid = research_mode.run_research(
        {"enabled": True, "offline": False, "adapter": "openrouter"},
        ["https://example.test/public/note"],
    )
    assert paid["observed_claims"] == []
    assert paid["rejected"][0]["reason"] == "paid_adapter_opt_in"


def test_offline_still_skips_the_adapter() -> None:
    class Spy(research_mode.NullAdapter):
        calls = 0

        def gather(self, queries: list[str]) -> list[dict]:
            self.calls += 1
            return [{"url": "https://example.test/x", "text": "nope", "retrieved_at": "2026-10-01", "complete": True}]

    spy = Spy()
    result = research_mode.run_research(
        {"enabled": False, "offline": True, "adapter": "robots_http"},
        ["https://example.test/x"],
        adapter=spy,
    )
    assert spy.calls == 0
    assert result["observed_claims"] == []


def test_tie_breaker_runs_only_on_disagreement() -> None:
    packets = [
        {"id": "left-arm", "body": "The buyer is NOT_COMPUTABLE and no price is set."},
        {"id": "right-arm", "body": "An illustrative hosted tier is proposed."},
    ]
    scores = {name: 1.0 for name in judge_eval.ALL_CRITERIA}

    def judge(name: str, excerpt: str) -> judge_eval.FixtureTableJudge:
        return judge_eval.load_judge(
            {
                "kind": "fixture",
                "name": name,
                "winner_excerpt": excerpt,
                "default_scores": scores,
                "rows": [],
            }
        )

    agree_breaker = judge("tie", "NOT_COMPUTABLE")
    original = agree_breaker.prefer
    calls = {"n": 0}

    def counting(left: str, right: str) -> str:
        calls["n"] += 1
        return original(left, right)

    agree_breaker.prefer = counting  # type: ignore[method-assign]
    agreed = judge_eval.run_panel(
        packets,
        [judge("one", "NOT_COMPUTABLE"), judge("two", "NOT_COMPUTABLE")],
        seed=1,
        tie_breaker=agree_breaker,
    )
    assert agreed["disagreement"] is False
    assert agreed["tie_breaker_invoked"] is False
    assert calls["n"] == 0
    assert judge_eval.agreed_source(agreed) == "left-arm"

    split = judge_eval.run_panel(
        packets,
        [judge("one", "NOT_COMPUTABLE"), judge("two", "hosted tier")],
        seed=1,
        tie_breaker=agree_breaker,
    )
    assert split["disagreement"] is True
    assert split["tie_breaker_invoked"] is True
    assert calls["n"] == 2
    assert judge_eval.agreed_source(split) == "left-arm"
    assert split["model_invoked"] is False


def test_legacy_v12_sample_still_validates() -> None:
    proc = subprocess.run(
        [PY, str(VALIDATE), "--packet", str(SAMPLE_V12), "--type", "opportunity"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stderr
    packet = packet_compose.seat_option_example_packet()
    assert packet["schema_version"] == "1.3.0"
    checked = subprocess.run(
        [PY, str(VALIDATE), "--packet", "-", "--type", "opportunity"],
        cwd=ROOT,
        input=json.dumps(packet),
        text=True,
        capture_output=True,
    )
    # validate_packet may not read stdin. Fall through to packaging_errors.
    errors = packet_compose.packaging_errors(packet, "opportunity")
    assert errors == [], errors
    blob = json.dumps(packet)
    assert "BEGIN PRIVATE" not in blob
    assert "sk-" not in blob


def main() -> None:
    test_reconstructed_note_defects()
    print("PASS: test_reconstructed_note_defects")
    test_magnitude_suffix_is_not_stripped()
    print("PASS: test_magnitude_suffix_is_not_stripped")
    test_kill_recompute_includes_fee_and_every_tier()
    print("PASS: test_kill_recompute_includes_fee_and_every_tier")
    test_placeholder_date_and_quote_support()
    print("PASS: test_placeholder_date_and_quote_support")
    test_robots_fetch_is_free_and_fail_closed()
    print("PASS: test_robots_fetch_is_free_and_fail_closed")
    test_offline_still_skips_the_adapter()
    print("PASS: test_offline_still_skips_the_adapter")
    test_tie_breaker_runs_only_on_disagreement()
    print("PASS: test_tie_breaker_runs_only_on_disagreement")
    test_legacy_v12_sample_still_validates()
    print("PASS: test_legacy_v12_sample_still_validates")
    print("PASS: bake-off round 2")


if __name__ == "__main__":
    main()
