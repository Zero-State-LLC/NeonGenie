#!/usr/bin/env python3
"""v3.33 bake-off fixes. Stdlib only. No network and no paid model calls.

The main page keeps named money-table recomputes, contradictory web facts,
and at most five primary links. Jev is mocked. Search junk is not OBSERVED.
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
        "notes say Heavy per tenant 636, recomputed Shared Heavy 336.4"
    ], money
    blob = "\n".join(
        row["summary"] for row in scanned["findings"] + scanned["unverified_notes"]
    )
    assert "331.5" not in blob
    assert "Double of 64 is 128, not 512" not in blob
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
    assert main == money
    prose = packet_compose.prose_main(wrapped)
    assert money[0] in prose
    assert "331.5" not in prose
    assert "Computed 512" not in prose
    assert wrapped["build_handoff"]["first_commit"]["touch"] == ["pricing notes"]
    alta = packet_compose.scan_input_notes(rows["alta_burn_rent"])
    assert any(
        row["summary"] == "notes say monthly burn 35000, recomputed monthly rent 55000"
        for row in alta["findings"]
    )
    print("one named recompute; duplicate 331.5 dropped; burn versus rent named")


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
    assert len(result["observed_claims"]) == 1
    claim = result["observed_claims"][0]
    assert claim["label"] == "OBSERVED"
    assert claim["url"] == rows["primary"]["url"]
    reasons = {row["reason"] for row in result["unverified_hits"]}
    assert reasons == {"error_page", "social", "fragment"}
    assert all(row["claim_label"] == "NOT_COMPUTABLE" for row in result["unverified_hits"])
    assert all(row["status"] == "unverified" for row in result["unverified_hits"])
    urls = {row["url"] for row in result["unverified_hits"]}
    assert rows["not_found"]["url"] in urls
    assert rows["instagram"]["url"] in urls
    wrapped = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": {"checked": True, "findings": []},
            "research": result,
        }
    )
    prose = packet_compose.prose_main(wrapped)
    assert rows["primary"]["url"] in prose
    assert "instagram.com" not in prose
    assert "Not found" not in prose
    parked = wrapped["appendix"]["search_hits_not_used"]["hits"]
    assert {row["url"] for row in parked} == urls
    assert wrapped["page_budget"]["fits_one_page"] is True
    print("Not found, Instagram, and a fragment are unverified; primary stays OBSERVED")


def test_main_page_lists_at_most_five_links() -> None:
    cite = _rows()["primary"]["text"]
    claims = []
    for index in range(8):
        claims.append(
            {
                "claim_id": f"obs-{index + 1}",
                "label": "OBSERVED",
                "kind": "web_page",
                "url": f"https://example.test/pricing/plan-{index}",
                "retrieved_at": "2026-10-01",
                "text": cite,
            }
        )
    packet = packet_compose.apply_page_budget(
        {
            "opportunity_thesis": "Short thesis.",
            "input_contradictions": {"checked": True, "findings": []},
            "research": {"observed_claims": claims},
        }
    )
    prose = packet_compose.prose_main(packet)
    assert prose.count("https://") == packet_compose.MAIN_LINK_CAP
    assert packet["page_budget"]["fits_one_page"] is True
    assert packet["page_budget"]["main_word_count"] <= packet_compose.WORD_BUDGET
    print("main page lists five primary links")


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
    assert "CONTRADICTS:" in prose
    assert "AGREES:" not in prose
    parked = packet["appendix"]["fact_reconcile"]["items"]
    assert any(row["verdict"] == "AGREES" for row in parked)
    assert all(row["verdict"] != "CONTRADICTS" for row in parked)

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
    print("Jev reconcile mocked; contradicts on the main page; cap holds; no live call")


def main() -> None:
    test_duplicate_line_keeps_one_named_recompute()
    test_not_found_and_instagram_are_not_observed()
    test_main_page_lists_at_most_five_links()
    test_jev_reconcile_is_mocked_and_capped()
    print("PASS: bake-off v3.33")


if __name__ == "__main__":
    main()
