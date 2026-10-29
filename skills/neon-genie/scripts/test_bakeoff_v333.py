#!/usr/bin/env python3
"""v3.33 checks, updated for v3.34. Stdlib only. No network and no paid calls.

Named money recomputes stay on the main page. Search hits and Jev lines
do not. None of those research rows are OBSERVED.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import jev_client
import judge_eval
import packet_compose
import research_mode

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "evals" / "fixtures" / "v333" / "regressions.json"


def _rows() -> dict:
    return json.loads(FIX.read_text(encoding="utf-8"))


def _quiet() -> None:
    os.environ.pop(jev_client.ENV_KEY, None)
    os.environ.pop(research_mode.PAID_KEY_ENV, None)
    os.environ.pop(research_mode.PAID_FLAG_ENV, None)
    os.environ.pop(research_mode.FIRECRAWL_KEY_ENV, None)


def test_duplicate_line_keeps_one_named_recompute() -> None:
    rows = _rows()
    scanned = packet_compose.scan_input_notes(rows["duplicate_line"])
    summaries = [row["summary"] for row in scanned["findings"]]
    money = [summary for summary in summaries if summary.startswith("notes say ")]
    assert money == [
        "notes say Cove per tenant 425, recomputed Pooled cove 225"
    ], money
    blob = "\n".join(
        row["summary"] for row in scanned["findings"] + scanned["unverified_notes"]
    )
    assert "Double of 40 is 80, not 160" not in blob
    wrapped = packet_compose.apply_page_budget(
        {
            "input_contradictions": scanned,
            "research": {"observed_claims": []},
            "build_handoff": {
                "summary": "Ship the notes check.",
                "first_commit": {
                    "touch": ["pricing notes"],
                    "done_when": "One seat rule is declared.",
                    "test_to_write": "Re-run the input pass.",
                    "owner_role": "operator",
                },
            },
        }
    )
    main = [row["summary"] for row in wrapped["input_contradictions"]["findings"]]
    assert main.count(money[0]) == 1
    assert "Computed 160 does not appear in a later total." in main
    prose = packet_compose.prose_main(wrapped)
    assert money[0] in prose
    assert prose.count(money[0]) == 1
    assert prose.count("Computed 160 does not appear in a later total.") == 1
    assert wrapped["build_handoff"]["first_commit"]["touch"] == ["pricing notes"]
    yard = packet_compose.scan_input_notes(rows["yard_burn_rent"])
    assert any(
        row["summary"] == "notes say monthly burn 18000, recomputed monthly rent 32000"
        for row in yard["findings"]
    )
    print("one named recompute; false double dropped; burn versus rent named")


class _Provider:
    name = "paid_search"

    def __init__(self, hits: list[dict]) -> None:
        self.hits = hits
        self.calls = 0

    def search(self, query: str) -> list[dict]:
        self.calls += 1
        return self.hits


def test_not_found_and_instagram_are_not_observed() -> None:
    _quiet()
    rows = _rows()
    hits = []
    for key in ("not_found", "instagram", "fragment", "primary"):
        item = dict(rows[key])
        item.update({"complete": True, "retrieved_at": "2026-10-01", "kind": "web_page"})
        hits.append(item)
    provider = _Provider(hits)
    result = research_mode.run_idea_research(
        {
            "enabled": True,
            "offline": False,
            "adapter": "null",
            "allow_paid": True,
            "search_provider": provider,
            "paid_price_per_call": 0.01,
        },
        ["vendor pricing"],
    )
    assert provider.calls == 1
    assert result["observed_claims"] == []
    reasons = {row["reason"] for row in result["unverified_hits"]}
    assert reasons == {"error_page", "social", "fragment", "unreviewed"}
    assert all(row["claim_label"] == "NOT_COMPUTABLE" for row in result["unverified_hits"])
    assert all(row["status"] == "unreviewed" for row in result["unverified_hits"])
    assert all(row.get("label") != "OBSERVED" for row in result["unverified_hits"])
    urls = {row["url"] for row in result["unverified_hits"]}
    assert rows["not_found"]["url"] in urls
    assert rows["instagram"]["url"] in urls
    assert rows["primary"]["url"] in urls
    wrapped = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": {"checked": True, "findings": []},
            "research": result,
        }
    )
    prose = packet_compose.prose_main(wrapped)
    assert rows["primary"]["url"] not in prose
    assert "instagram.com" not in prose
    assert "Not found" not in prose
    assert "OBSERVED" not in prose
    parked = packet_compose.unreviewed_research(wrapped)
    assert parked is not None
    assert "research_unreviewed" not in wrapped.get("appendix", {})
    assert parked["label"] == "Research (unreviewed, needs a person's review)"
    assert {row["url"] for row in parked["search_hits"]} == urls
    assert all(row["claim_label"] != "OBSERVED" for row in parked["search_hits"])
    assert wrapped["page_budget"]["fits_one_page"] is True
    print("search hits are unreviewed and off the main page")


def test_search_links_stay_off_the_main_page() -> None:
    cite = _rows()["primary"]["text"]
    hits = []
    for index in range(8):
        hits.append(
            {
                "url": f"https://example.test/pricing/plan-{index}",
                "text": cite,
                "retrieved_at": "2026-10-01",
                "reason": "unreviewed",
                "status": "unreviewed",
                "claim_label": "NOT_COMPUTABLE",
            }
        )
    packet = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": {"checked": True, "findings": []},
            "research": {"observed_claims": [], "unverified_hits": hits},
        }
    )
    prose = packet_compose.prose_main(packet)
    assert "https://" not in prose
    assert packet["page_budget"]["fits_one_page"] is True
    assert packet["page_budget"]["main_word_count"] <= packet_compose.WORD_BUDGET
    parked_doc = packet_compose.unreviewed_research(packet)
    assert parked_doc is not None
    parked = parked_doc["search_hits"]
    assert len(parked) == 8
    assert all(row["claim_label"] == "NOT_COMPUTABLE" for row in parked)
    print("search links stay off the main page")


def _client(choice_for: dict[str, str]) -> tuple[list[int], object]:
    calls: list[int] = []

    def client(state: str, questions: dict) -> dict:
        if "https://" in state and "api.typesafe.ai" in state:
            raise AssertionError("live Jev URL in state")
        calls.append(1)
        answers = {}
        for key in questions:
            if key.startswith("v"):
                answers[key] = {"choice": choice_for.get(key, "NOT_APPLICABLE")}
            else:
                answers[key] = {"choice": "S001"}
        return {"model": "jev-test", "answers": answers}

    return calls, client


def test_jev_reconcile_is_mocked_and_capped() -> None:
    _quiet()

    def boom(*_args: object, **_kwargs: object) -> dict:
        raise AssertionError("live Jev call")

    jev_client.system_one = boom  # type: ignore[method-assign]
    notes = "Heavy seat is about $300 per month.\nSupabase Pro is $25 per month."
    cite = _rows()["primary"]["text"]
    claims = [
        {
            "claim_id": "obs-1",
            "label": "OBSERVED",
            "url": "https://example.test/pricing",
            "text": "SuperGrok lists $30 per month. " + cite,
        },
        {
            "claim_id": "obs-2",
            "label": "OBSERVED",
            "url": "https://example.test/docs/billing",
            "text": cite,
        },
    ]
    absent = judge_eval.reconcile_facts(notes, claims)
    assert absent["calls"] == 0
    assert absent["status"] == "NOT_COMPUTABLE"
    assert all(row["verdict"] == "NOT_COMPUTABLE" for row in absent["items"])
    assert all("AGREES" not in row["sentence"] for row in absent["items"])
    assert all("CONTRADICTS" not in row["sentence"] for row in absent["items"])

    calls, client = _client({"v0": "CONTRADICTS", "v1": "AGREES"})
    result = judge_eval.reconcile_facts(notes, claims, client=client)
    assert calls == [1]
    assert result["calls"] == 1
    contradicted = result["items"][0]
    agreed = result["items"][1]
    assert contradicted["verdict"] == "CONTRADICTS"
    assert agreed["verdict"] == "AGREES"
    assert 'Note: "Heavy seat is about $300 per month."' in contradicted["sentence"]
    assert contradicted["sentence"].startswith("CONTRADICTS:")
    packet = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": {"checked": True, "findings": []},
            "research": {"observed_claims": claims, "reconcile": result},
        }
    )
    prose = packet_compose.prose_main(packet)
    assert "CONTRADICTS:" not in prose
    assert "AGREES:" not in prose
    assert "OBSERVED" not in prose
    parked = packet_compose.unreviewed_research(packet)
    assert parked is not None
    assert "research_unreviewed" not in packet.get("appendix", {})
    assert parked["label"] == "Research (unreviewed, needs a person's review)"
    verdicts = {row["verdict"] for row in parked["reconcile"]}
    assert verdicts == {"AGREES", "CONTRADICTS"}
    assert all(row.get("claim_label") != "OBSERVED" for row in parked["reconcile"])

    more = claims + [
        {
            "claim_id": "obs-3",
            "label": "OBSERVED",
            "url": "https://example.test/docs/extra",
            "text": cite,
        },
        {
            "claim_id": "obs-4",
            "label": "OBSERVED",
            "url": "https://arxiv.org/abs/example",
            "text": cite,
        },
    ]
    capped_calls, capped_client = _client({})
    capped = judge_eval.reconcile_facts(
        notes, more, client=capped_client, max_calls=1, per_call=1
    )
    assert capped_calls == [1]
    assert capped["calls"] == 1
    assert sum(row["reason"] == "jev_call_cap" for row in capped["items"]) == 3
    print("Jev reconcile mocked; every verdict is in the appendix; cap holds; no live call")


def test_reconcile_step_stays_off_without_the_paid_flag() -> None:
    _quiet()
    calls: list[int] = []

    def client(state: str, questions: dict) -> dict:
        calls.append(1)
        return {"model": "jev-test", "answers": {}}

    packet = packet_compose.attach_v12(
        {"opportunity_thesis": "Short thesis."},
        notes="Heavy seat is about $300 per month.",
        research_policy={
            "enabled": True,
            "offline": False,
            "adapter": "fixture",
            "jev_client": client,
        },
        queries=["seat floor"],
        schema_id="neon-genie/opportunity-packet",
        adapter=research_mode.FixtureAdapter(
            [
                {
                    "url": "https://example.test/fixtures/seat-floor",
                    "retrieved_at": "2026-10-01",
                    "complete": True,
                    "kind": "web_page",
                    "text": "Fixture page states no live price.",
                    "query": "seat floor",
                }
            ]
        ),
        handoff={
            "summary": "Reconcile the notes.",
            "first_commit": {
                "touch": ["notes"],
                "done_when": "One rule is declared.",
                "test_to_write": "Re-run the input pass.",
                "owner_role": "operator",
            },
        },
        kill_criteria=[
            {
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
    assert calls == []
    assert "reconcile" not in packet["research"]
    prose = packet_compose.prose_main(packet)
    assert "https://" not in prose
    print("Jev reconcile stays off without NEON_GENIE_RESEARCH_PAID")


def main() -> None:
    test_duplicate_line_keeps_one_named_recompute()
    test_not_found_and_instagram_are_not_observed()
    test_search_links_stay_off_the_main_page()
    test_jev_reconcile_is_mocked_and_capped()
    test_reconcile_step_stays_off_without_the_paid_flag()
    print("PASS: bake-off v3.33")


if __name__ == "__main__":
    main()
