#!/usr/bin/env python3
"""Score packets with two independent judges and an optional tie-breaker.

Neutral criteria sit beside Neon Genie's own criteria. Order is shuffled and
pairwise choices run in both A/B directions. A third judge runs only when the
first two disagree on the pairwise winner. The panel does not call a model.

``judge_correctness`` is a separate optional diagnostic. It is off unless the
caller passes ``enabled=True``. When on, it asks Jev (TypeSafe System One)
which line is wrong. Jev returns a line id, not prose; this module quotes the
line those ids point at. Tests pass a mock client and do not touch the network.
"""

from __future__ import annotations

import random
import re
from typing import Any, Callable, Protocol

import jev_client

_LINE_CAP = 254

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


def _numbered_lines(text: str, prefix: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if len(rows) >= _LINE_CAP:
            break
        rows.append((f"{prefix}{index:03d}", line))
    return rows


def _choice_question(instructions: str, rows: list[tuple[str, str]]) -> dict[str, Any]:
    criteria: dict[str, Any] = {"none": "No line applies"}
    for line_id, line in rows:
        preview = line.strip()
        criteria[line_id] = preview[:180] if preview else "(blank line)"
    return {
        "type": "choice",
        "instructions": instructions,
        "criteria": criteria,
    }


def judge_correctness(
    document: str,
    source_notes: str,
    *,
    enabled: bool = False,
    client: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Optional correctness diagnostic. Off by default. No network unless enabled.

    Jev cannot return a prose reason. The workable form is a line-id Choice:
    the model picks a document line id and a SOURCE_NOTES line id, and this
    function quotes those lines from the text it sent.
    """
    base: dict[str, Any] = {
        "enabled": bool(enabled),
        "invoked": False,
        "model_invoked": False,
        "reason_form": "line_id_choice",
        "prose_reasons": False,
        "has_conflict": None,
        "document_line_id": None,
        "document_line": None,
        "source_line_id": None,
        "source_line": None,
    }
    if not enabled:
        base["reason"] = "disabled"
        return base
    doc_rows = _numbered_lines(document if isinstance(document, str) else "", "D")
    src_rows = _numbered_lines(source_notes if isinstance(source_notes, str) else "", "S")
    state = "\n".join(
        ["DOCUMENT"]
        + [f"{line_id}| {line}" for line_id, line in doc_rows]
        + ["SOURCE_NOTES"]
        + [f"{line_id}| {line}" for line_id, line in src_rows]
    )
    questions = {
        "has_conflict": {
            "type": "noul",
            "instructions": (
                "Does any DOCUMENT line conflict with a SOURCE_NOTES line?"
            ),
            "criteria": {
                "true": "A document line states something the notes contradict",
                "false": "No document line conflicts with the notes",
            },
        },
        "document_line": _choice_question(
            "Which DOCUMENT line is wrong? Choose none if no line is wrong.",
            doc_rows,
        ),
        "source_line": _choice_question(
            "Which SOURCE_NOTES line conflicts with that document line? "
            "Choose none if none conflicts.",
            src_rows,
        ),
    }
    call = client or jev_client.system_one
    try:
        response = call(state, questions)
    except jev_client.JevError as exc:
        base["reason"] = str(exc)
        return base
    if not isinstance(response, dict):
        base["reason"] = "Jev returned a non-object"
        return base
    answers = response.get("answers")
    if not isinstance(answers, dict):
        base["reason"] = "Jev returned no answers"
        return base
    base["invoked"] = True
    base["model_invoked"] = True
    base["model"] = response.get("model")
    conflict = answers.get("has_conflict") or {}
    noul = conflict.get("noul") if isinstance(conflict, dict) else None
    if isinstance(noul, (int, float)) and not isinstance(noul, bool):
        base["has_conflict"] = float(noul) >= 0.5
    doc_choice = _choice_id(answers.get("document_line"))
    src_choice = _choice_id(answers.get("source_line"))
    doc_map = dict(doc_rows)
    src_map = dict(src_rows)
    base["document_line_id"] = doc_choice
    base["source_line_id"] = src_choice
    if doc_choice in doc_map:
        base["document_line"] = doc_map[doc_choice]
    if src_choice in src_map:
        base["source_line"] = src_map[src_choice]
    doc_answer = answers.get("document_line")
    if isinstance(doc_answer, dict) and isinstance(doc_answer.get("confidence"), (int, float)):
        base["confidence"] = float(doc_answer["confidence"])
    return base


def _choice_id(answer: Any) -> str | None:
    if not isinstance(answer, dict):
        return None
    choice = answer.get("choice")
    if not isinstance(choice, str) or choice == "none":
        return None
    return choice


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
