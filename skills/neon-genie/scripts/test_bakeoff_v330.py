#!/usr/bin/env python3
"""v3.30 bake-off fixes. Stdlib only. No network and no paid calls.

Fixtures are the round 2–3 cases in evals/bakeoff-v330/. The note-scan
catch rate is measured by scripts/eval_note_scan.py; this file does not
add idea-specific phrases to the scanner.
"""

from __future__ import annotations

import io
import json
import urllib.error
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import eval_note_scan
import judge_eval
import packet_compose
import research_mode

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "evals" / "bakeoff-v330"
CASES = json.loads((FIX / "fixtures-v330.json").read_text(encoding="utf-8"))


def _quote_ok(got: str, expect: str) -> bool:
    if "must NOT be supports" in expect or expect.startswith("not supports"):
        return got != "supports"
    if expect.startswith("supports"):
        return got == "supports"
    if expect.startswith("contradicts"):
        return got == "contradicts"
    return False


def test_quote_cases() -> None:
    rows = CASES["fix1_quote_cases"]
    assert len(rows) == 6
    correct = 0
    for row in rows:
        got = packet_compose.quote_support(row["claim"], row["quote"])
        ok = _quote_ok(got, row["expect"])
        assert ok, (row["claim"], got, row["expect"])
        if ok:
            correct += 1
    assert correct == 6
    print(f"fix1 quote cases {correct}/6")


def test_alta_note_placeholder() -> None:
    kill = CASES["fix2_alta_note_placeholder"]["kill"]
    packet = {"schema_version": "1.2.0", "kill_criteria": [kill]}
    errors = packet_compose.packaging_errors(packet, "opportunity")
    assert any(line.startswith("NG-LABEL-001") for line in errors), errors
    # A real date on the field is not enough when the note says placeholder.
    assert "placeholder" in kill["note"]
    print("fix2 Alta note placeholder: caught")


def _autogive_packet(threshold: float, derivation: dict) -> dict:
    return {
        "schema_version": "1.3.0",
        "opportunity_thesis": (
            "SKU 1 list ESTIMATE $500 and $650 tiers. "
            "Stripe 2.9% + $0.30 card fee."
        ),
        "kill_criteria": [
            {
                "metric": "projected_monthly_token_cost_usd",
                "threshold": threshold,
                "comparison": "gt",
                "check_date": "2026-10-14",
                "data_source": "metered export",
                "claim_label": "INFERRED",
                "derivation": derivation,
            }
        ],
    }


def test_autogive_cost_inputs() -> None:
    correct = 0
    for row in CASES["fix3_autogive_170"]["cases"]:
        packet = _autogive_packet(row["threshold"], row["derivation"])
        errors = packet_compose.packaging_errors(packet, "opportunity")
        kill_errors = [
            line
            for line in errors
            if line.startswith("NG-KILL-004") or line.startswith("NG-KILL-006")
        ]
        expect = row["expect"]
        if expect == "pass":
            ok = kill_errors == []
        elif expect.startswith("NG-KILL-004"):
            ok = any(line.startswith("NG-KILL-004") for line in kill_errors)
        else:
            ok = any(line.startswith("NG-KILL-006") for line in kill_errors)
        assert ok, (expect, kill_errors)
        correct += 1
    justified = _autogive_packet(
        170,
        {
            "formula": "identity",
            "inputs": {"value": 170},
            "depends_on": ["value"],
            "justification": (
                "Taken as-is: the operator set 170 before card fees on purpose."
            ),
        },
    )
    justified_errors = [
        line
        for line in packet_compose.packaging_errors(justified, "opportunity")
        if line.startswith("NG-KILL-006")
    ]
    assert justified_errors == []
    full = json.loads(
        (FIX / "r3-packets" / "3-harbor-seat-plan.opportunity.packet.json").read_text(
            encoding="utf-8"
        )
    )
    full_errors = [
        line
        for line in packet_compose.packaging_errors(full, "opportunity")
        if line.startswith("NG-KILL-004") or line.startswith("NG-KILL-006")
    ]
    assert full_errors == [], full_errors
    assert correct == 3
    print(f"fix3 Autogive cases {correct}/3")


def test_note_scan_is_general() -> None:
    source = (ROOT / "scripts" / "packet_compose.py").read_text(encoding="utf-8")
    for phrase in (
        "plugin-to-paid funnel",
        "x402 fits agents",
        "one build serves all three",
        "contracts or keys",
        "Operator seat is included",
    ):
        assert phrase not in source, phrase
    caught = eval_note_scan.catch_report()
    fps = eval_note_scan.false_positive_report()
    held = eval_note_scan.held_out_report()
    assert caught["total"] == 16
    assert fps["synthetic_findings"] == 0, fps["synthetic"]
    assert fps["doc_findings"] == 0, fps["docs"]
    assert held["planted_caught"] == held["planted"], held
    assert held["clean_findings"] == 0, held
    print(
        f"fix4 catch {caught['caught']}/{caught['total']} "
        f"false_positives docs={fps['doc_findings']} synthetic={fps['synthetic_findings']} "
        f"held_out {held['planted_caught']}/{held['planted']} "
        f"clean_findings={held['clean_findings']}"
    )
    for row in caught["issues"]:
        mark = "hit" if row["caught"] else "miss"
        print(f"  {row['id']} {mark}")
    if fps["docs"]:
        print("doc findings:")
        for row in fps["docs"]:
            print(f"  {row['path']}: {row['summary']}")


class _Page:
    def __init__(self, body: bytes, url: str, status: int = 200) -> None:
        self._body = body
        self.status = status
        self._url = url

    def read(self, n: int = -1) -> bytes:
        if n < 0 or n >= len(self._body):
            return self._body
        return self._body[:n]

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> _Page:
        return self

    def __exit__(self, *_exc: object) -> bool:
        return False


def test_robots_404_cap_and_la_date() -> None:
    calls: list[str] = []

    def opener(req: object, timeout: int = 10) -> _Page:
        assert timeout == 10
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()  # type: ignore[union-attr]
        calls.append(url)
        if url.endswith("/robots.txt"):
            raise urllib.error.HTTPError(
                url,
                404,
                "Not Found",
                EmailMessage(),
                io.BytesIO(b"missing"),
            )
        return _Page(b"readme body", url)

    adapter = research_mode.RobotsHttpAdapter(opener=opener)
    allowed, reason = adapter._allowed(
        "https://raw.githubusercontent.com/x/y/main/README.md"
    )
    assert allowed is True, reason
    assert reason == ""
    gathered = adapter.gather(["https://raw.githubusercontent.com/x/y/main/README.md"])
    assert gathered[0]["complete"] is True
    assert gathered[0]["text"] == "readme body"

    def status_404(req: object, timeout: int = 10) -> _Page:
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()  # type: ignore[union-attr]
        if str(url).endswith("/robots.txt"):
            return _Page(b"missing", str(url), status=404)
        return _Page(b"page", str(url))

    status_adapter = research_mode.RobotsHttpAdapter(opener=status_404)
    ok, why = status_adapter._allowed("https://example.test/readme")
    assert (ok, why) == (True, "")

    big = b"y" * 100_000
    assert len(big) > 65536
    assert len(big) < research_mode.MAX_BODY_BYTES

    def wide(req: object, timeout: int = 10) -> _Page:
        return _Page(big, "https://example.test/pricing")

    fetched = research_mode.fetch_url("https://example.test/pricing", opener=wide)
    assert fetched["complete"] is True
    assert fetched["reason"] if False else fetched.get("reason") is None
    assert len(fetched["text"]) == 100_000

    def over(req: object, timeout: int = 10) -> _Page:
        return _Page(b"z" * (research_mode.MAX_BODY_BYTES + 8), "https://example.test/huge")

    capped = research_mode.fetch_url("https://example.test/huge", opener=over)
    assert capped["complete"] is False
    assert capped["reason"] == "body_cap"
    assert "text" not in capped
    # 2026-09-30 22:45 PT is 2026-10-01 05:45 UTC.
    stamped = research_mode._today(datetime(2026, 10, 1, 5, 45, tzinfo=timezone.utc))
    assert stamped == "2026-09-30"
    assert research_mode.MAX_BODY_BYTES == 2 * 1024 * 1024
    print("fix5 robots 404 allowed, body cap 2 MiB, retrieved_at America/Los_Angeles")


def test_correctness_judge_quotes_lines() -> None:
    off = judge_eval.judge_correctness(
        "The threshold is $170.",
        "Tiers are $500 and $650.",
    )
    assert off["enabled"] is False
    assert off["invoked"] is False
    assert off["model_invoked"] is False

    document = "Line one is fine.\nThe threshold is $170.\nLine three is fine."
    notes = "Intro.\nTiers are $500 and $650 before the card fee."

    def client(state: str, questions: dict) -> dict:
        assert "D002|" in state
        assert "S002|" in state
        assert questions["document_line"]["type"] == "choice"
        assert questions["source_line"]["type"] == "choice"
        assert questions["has_conflict"]["type"] == "noul"
        return {
            "model": "jev-test",
            "answers": {
                "has_conflict": {"type": "noul", "noul": 0.91},
                "document_line": {
                    "type": "choice",
                    "choice": "D002",
                    "confidence": 0.8,
                    "probabilities": {"D002": 0.8, "none": 0.2},
                },
                "source_line": {
                    "type": "choice",
                    "choice": "S002",
                    "confidence": 0.7,
                    "probabilities": {"S002": 0.7, "none": 0.3},
                },
            },
        }

    judged = judge_eval.judge_correctness(document, notes, enabled=True, client=client)
    assert judged["invoked"] is True
    assert judged["prose_reasons"] is False
    assert judged["reason_form"] == "line_id_choice"
    assert judged["document_line"] == "The threshold is $170."
    assert judged["source_line"] == "Tiers are $500 and $650 before the card fee."
    assert judged["has_conflict"] is True

    missing = research_mode  # keep the import used
    assert missing.MAX_BODY_BYTES
    try:
        import os

        saved = os.environ.pop("TYPESAFE_AI_API_KEY", None)
        try:
            import jev_client

            jev_client.system_one("state", {"q": {"type": "noul", "instructions": "x"}})
            raise AssertionError("missing key should fail")
        except jev_client.JevError as exc:
            assert "TYPESAFE_AI_API_KEY" in str(exc)
            assert "secret-token" not in str(exc)
        finally:
            if saved is not None:
                os.environ["TYPESAFE_AI_API_KEY"] = saved
    except Exception:
        raise
    print("fix6 line-id quotes; diagnostic off by default")


def main() -> None:
    test_quote_cases()
    test_alta_note_placeholder()
    test_autogive_cost_inputs()
    test_note_scan_is_general()
    test_robots_404_cap_and_la_date()
    test_correctness_judge_quotes_lines()
    print("PASS: bake-off v3.30")


if __name__ == "__main__":
    main()
