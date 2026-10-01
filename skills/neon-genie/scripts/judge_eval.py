#!/usr/bin/env python3
"""Score packets with two or more independent judges.

Neutral criteria sit beside Neon Genie's own criteria. Order is shuffled and
pairwise choices run in both A/B directions. This module does not call a
model or the network. CI uses fixture judges only.
"""

from __future__ import annotations

import random
import re
from typing import Any, Protocol

NEUTRAL_CRITERIA = (
    "founder_usefulness",
    "correctness",
    "actionability",
)
NG_CRITERIA = (
    "labeled_claims",
    "no_invented_buyers_or_prices",
    "kill_criteria_testable",
    "cheapest_falsifying_test",
    "build_handoff",
    "evidence_from_sources",
)
ALL_CRITERIA = NEUTRAL_CRITERIA + NG_CRITERIA

_BRANDS = (
    "Neon Genie",
    "NeonGenie",
    "neon-genie",
    "Deep Research",
    "ChatGPT",
    "OpenRouter",
    "Opus",
)
_PAID_KINDS = frozenset(
    {"paid", "openrouter", "anthropic", "openai", "http", "network"}
)


class JudgeRejected(ValueError):
    """A judge spec is not allowed in this harness."""


class Judge(Protocol):
    name: str

    def score(self, document: str, criteria: tuple[str, ...]) -> dict[str, float]:
        """Score one debranded document. No other judge's scores are provided."""

    def prefer(self, left: str, right: str) -> str:
        """Return 'left' or 'right' for this presentation order."""


def debrand(text: str) -> str:
    out = text
    for brand in _BRANDS:
        out = re.sub(re.escape(brand), "arm", out, flags=re.IGNORECASE)
    return out


class FixtureTableJudge:
    """Scores from a caller-supplied table. The table is the fixture, not an API."""

    def __init__(
        self,
        name: str,
        rows: list[dict[str, Any]],
        default_scores: dict[str, Any],
        winner_excerpt: str = "",
    ) -> None:
        self.name = name
        self.rows = list(rows)
        self.default_scores = dict(default_scores)
        self.winner_excerpt = winner_excerpt

    def score(self, document: str, criteria: tuple[str, ...]) -> dict[str, float]:
        chosen = self.default_scores
        for row in self.rows:
            excerpt = str(row.get("excerpt") or "")
            if excerpt and excerpt in document:
                chosen = row
                break
        return {criterion: float(chosen[criterion]) for criterion in criteria}

    def prefer(self, left: str, right: str) -> str:
        if self.winner_excerpt and self.winner_excerpt in left:
            return "left"
        if self.winner_excerpt and self.winner_excerpt in right:
            return "right"
        return "left"


def load_judge(spec: dict[str, Any]) -> Judge:
    kind = str(spec.get("kind") or "")
    if kind in _PAID_KINDS:
        raise JudgeRejected(
            "NG-JUDGE-001: paid or networked judges are disabled in this harness"
        )
    if kind != "fixture":
        raise JudgeRejected(f"NG-JUDGE-002: unknown judge kind {kind!r}")
    default_scores = spec.get("default_scores")
    if not isinstance(default_scores, dict):
        raise JudgeRejected("NG-JUDGE-002: fixture judge needs default_scores")
    rows = spec.get("rows") or []
    if not isinstance(rows, list):
        raise JudgeRejected("NG-JUDGE-002: fixture rows must be a list")
    return FixtureTableJudge(
        name=str(spec.get("name") or "fixture-judge"),
        rows=rows,
        default_scores=default_scores,
        winner_excerpt=str(spec.get("winner_excerpt") or ""),
    )


def _blind_packets(
    packets: list[dict[str, Any]], seed: int
) -> list[dict[str, str]]:
    order = [dict(packet) for packet in packets]
    random.Random(seed).shuffle(order)
    blinded: list[dict[str, str]] = []
    for index, packet in enumerate(order):
        blinded.append(
            {
                "blind_id": chr(ord("A") + index),
                "source_id": str(packet.get("id") or ""),
                "body": debrand(str(packet.get("body") or "")),
            }
        )
    return blinded


def _preferred_id(choice: str, left_id: str, right_id: str) -> str:
    if choice == "left":
        return left_id
    if choice == "right":
        return right_id
    raise JudgeRejected("NG-JUDGE-003: prefer must return left or right")


def run_panel(
    packets: list[dict[str, Any]],
    judges: list[Judge],
    *,
    seed: int,
    criteria: tuple[str, ...] = ALL_CRITERIA,
) -> dict[str, Any]:
    """Score independently, then pairwise in both orders. No model call."""
    if len(judges) < 2:
        raise JudgeRejected("NG-JUDGE-004: panel needs two independent judges")
    if len({judge.name for judge in judges}) != len(judges):
        raise JudgeRejected("NG-JUDGE-004: judge names must be distinct")
    blinded = _blind_packets(packets, seed)
    scores: list[dict[str, Any]] = []
    for judge in judges:
        for row in blinded:
            scores.append(
                {
                    "judge": judge.name,
                    "blind_id": row["blind_id"],
                    "scores": judge.score(row["body"], criteria),
                }
            )
    pairwise: list[dict[str, Any]] = []
    if len(blinded) >= 2:
        left, right = blinded[0], blinded[1]
        for judge in judges:
            prefer_ab = judge.prefer(left["body"], right["body"])
            prefer_ba = judge.prefer(right["body"], left["body"])
            pairwise.append(
                {
                    "judge": judge.name,
                    "order_ab": {
                        "left": left["blind_id"],
                        "right": right["blind_id"],
                        "prefer": prefer_ab,
                        "preferred_blind_id": _preferred_id(
                            prefer_ab, left["blind_id"], right["blind_id"]
                        ),
                    },
                    "order_ba": {
                        "left": right["blind_id"],
                        "right": left["blind_id"],
                        "prefer": prefer_ba,
                        "preferred_blind_id": _preferred_id(
                            prefer_ba, right["blind_id"], left["blind_id"]
                        ),
                    },
                }
            )
    return {
        "model_invoked": False,
        "judge_count": len(judges),
        "criteria": list(criteria),
        "neutral_criteria": list(NEUTRAL_CRITERIA),
        "blind_order": [row["blind_id"] for row in blinded],
        "source_by_blind": {row["blind_id"]: row["source_id"] for row in blinded},
        "scores": scores,
        "pairwise": pairwise,
        "debranded_bodies": {row["blind_id"]: row["body"] for row in blinded},
    }


def agreed_source(result: dict[str, Any]) -> str | None:
    """Source id when every swapped pairwise choice names the same packet."""
    source_by_blind = result.get("source_by_blind") or {}
    winners: set[str] = set()
    pairs = result.get("pairwise") or []
    if not pairs:
        return None
    for pair in pairs:
        for order_name in ("order_ab", "order_ba"):
            order = pair.get(order_name) or {}
            blind_id = order.get("preferred_blind_id")
            if blind_id not in source_by_blind:
                return None
            winners.add(source_by_blind[blind_id])
    if len(winners) == 1:
        return next(iter(winners))
    return None
