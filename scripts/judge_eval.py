#!/usr/bin/env python3
"""Score packets with two independent judges and an optional tie-breaker.

Neutral criteria sit beside Neon Genie's own criteria. Order is shuffled and
pairwise choices run in both A/B directions. A third judge runs only when the
first two disagree on the pairwise winner. This module does not call a model
or the network. CI uses fixture judges only.
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


def _pairwise_row(
    judge: Judge, left: dict[str, str], right: dict[str, str], *, tie_breaker: bool
) -> dict[str, Any]:
    prefer_ab = judge.prefer(left["body"], right["body"])
    prefer_ba = judge.prefer(right["body"], left["body"])
    return {
        "judge": judge.name,
        "tie_breaker": tie_breaker,
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


def _stable_source(pair: dict[str, Any], source_by_blind: dict[str, str]) -> str | None:
    winners: set[str] = set()
    for order_name in ("order_ab", "order_ba"):
        blind_id = (pair.get(order_name) or {}).get("preferred_blind_id")
        if blind_id not in source_by_blind:
            return None
        winners.add(source_by_blind[blind_id])
    if len(winners) == 1:
        return next(iter(winners))
    return None


def run_panel(
    packets: list[dict[str, Any]],
    judges: list[Judge],
    *,
    seed: int,
    criteria: tuple[str, ...] = ALL_CRITERIA,
    tie_breaker: Judge | None = None,
) -> dict[str, Any]:
    """Score independently, then pairwise in both orders. No model call.

    ``tie_breaker`` is asked only when the first two judges do not name the
    same pairwise winner. It is not one of the scoring judges.
    """
    if len(judges) < 2:
        raise JudgeRejected("NG-JUDGE-004: panel needs two independent judges")
    names = [judge.name for judge in judges]
    if tie_breaker is not None:
        names.append(tie_breaker.name)
    if len(set(names)) != len(names):
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
    source_by_blind = {row["blind_id"]: row["source_id"] for row in blinded}
    disagreement = False
    tie_breaker_invoked = False
    if len(blinded) >= 2:
        left, right = blinded[0], blinded[1]
        for judge in judges[:2]:
            pairwise.append(_pairwise_row(judge, left, right, tie_breaker=False))
        primary_winners = {
            _stable_source(pair, source_by_blind) for pair in pairwise
        }
        disagreement = None in primary_winners or len(primary_winners) != 1
        if disagreement and tie_breaker is not None:
            tie_breaker_invoked = True
            pairwise.append(_pairwise_row(tie_breaker, left, right, tie_breaker=True))
    return {
        "model_invoked": False,
        "judge_count": len(judges),
        "criteria": list(criteria),
        "neutral_criteria": list(NEUTRAL_CRITERIA),
        "blind_order": [row["blind_id"] for row in blinded],
        "source_by_blind": source_by_blind,
        "scores": scores,
        "pairwise": pairwise,
        "debranded_bodies": {row["blind_id"]: row["body"] for row in blinded},
        "disagreement": disagreement,
        "tie_breaker_invoked": tie_breaker_invoked,
    }


def agreed_source(result: dict[str, Any]) -> str | None:
    """Source id when the decisive pairwise choices name the same packet.

    When the first two judges disagree, only the tie-breaker's two orders count.
    """
    source_by_blind = result.get("source_by_blind") or {}
    pairs = result.get("pairwise") or []
    if not pairs:
        return None
    if result.get("disagreement"):
        decisive = [pair for pair in pairs if pair.get("tie_breaker")]
        if not decisive:
            return None
    else:
        decisive = [pair for pair in pairs if not pair.get("tie_breaker")]
    winners: set[str] = set()
    for pair in decisive:
        chosen = _stable_source(pair, source_by_blind)
        if chosen is None:
            return None
        winners.add(chosen)
    if len(winners) == 1:
        return next(iter(winners))
    return None
