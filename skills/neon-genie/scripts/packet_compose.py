#!/usr/bin/env python3
"""Shape opportunity and commercial packets after the 2026-09-30 bake-off.

Before the packet is written:

1. Scan input notes for contradictions, arithmetic errors, and inconsistent figures.
2. Optionally gather sources (see research_mode). Offline adds no OBSERVED claims.
3. Attach structured kill criteria and a first-commit handoff.
4. Keep decision prose inside one page. Evidence moves intact into ``appendix``.

Schema 1.2.0 opts into these checks. Older packets stay valid.
"""

from __future__ import annotations

import re
from typing import Any

import research_mode

SCHEMA_VERSION = "1.2.0"
WORD_BUDGET = 450
CHAR_BUDGET = 3200

_COMPARISONS = frozenset({"lt", "lte", "gt", "gte", "eq", "neq"})
_LABELS = frozenset({"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"})
_FINDING_KINDS = frozenset(
    {"contradiction", "arithmetic_error", "inconsistent_figure"}
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_EQ = re.compile(
    r"(?P<a>\d[\d,]*(?:\.\d+)?)\s*(?:×|x|\*)\s*\$?(?P<b>\d[\d,]*(?:\.\d+)?)\s*=\s*\$?(?P<c>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_SEAT = re.compile(
    r"N\s*=\s*(?P<n>\d+)[^.\n]{0,80}?(?P<seats>one|two|three|four|\d+)\s+seats?\b",
    re.IGNORECASE,
)
_OPTION_AFTER = re.compile(
    r"option\s+([A-Z])\b[^.\n]{0,80}?\b(locked|selected|chosen)\b",
    re.IGNORECASE,
)
_OPTION_BEFORE = re.compile(
    r"\b(locked|selected|chosen)\b[^.\n]{0,60}?\boption\s+(?:is\s+)?([A-Z])\b",
    re.IGNORECASE,
)
_RATIONALE = re.compile(
    r"rationale for locked\s+([A-Z])\b[^.\n]{0,80}?describes\s+([A-Z])(?:'s)?\b",
    re.IGNORECASE,
)
_RENT_MO = re.compile(
    r"\$(\d+(?:\.\d+)?)\s*/\s*sf\s*/\s*mo",
    re.IGNORECASE,
)
_RENT_YR = re.compile(
    r"\$(\d+(?:\.\d+)?)\s*/\s*sf\s*/\s*(?:yr|year)",
    re.IGNORECASE,
)
_LABELED_NUM = re.compile(
    r"(?P<label>price floor|weekly users|refundable deposit)\s*[:=]\s*\$?(?P<num>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4}

SEAT_OPTION_NOTES = """\
# Fixture notes — metered seat floor (synthetic)

These notes are fixture data for the contradiction pass. They are not a customer record.

## Seat floor
The Heavy floor table mixes seat assumptions.
N=1 $636 counts two seats.
N=10 counts one seat.
N=50 counts one seat.

| tenants | seats | per_seat | stated_floor |
| --- | --- | --- | --- |
| 1 | 2 | 318 | 636 |
| 10 | 1 | 318 | 3180 |
| 50 | 1 | 318 | 15900 |

## Option lock
03: Option A is locked.
11: Option B leftovers remain the locked plan.
19: The locked option is B.
28: The rationale for locked A describes B's leftover inventory.

## Arithmetic
The sketch says 10 × 5 = 100.
"""

FIXTURE_SOURCE = {
    "url": "https://example.test/fixtures/seat-floor",
    "retrieved_at": "2026-10-01",
    "complete": True,
    "kind": "web_page",
    "title": "Fixture seat-floor note",
    "query": "seat floor",
    "text": (
        "Fixture page: the Heavy floor table is operator-supplied "
        "and is not a market price."
    ),
}


def _num(token: str) -> float:
    return float(token.replace(",", "").replace("$", ""))


def _close(left: float, right: float) -> bool:
    scale = max(1.0, abs(left), abs(right))
    return abs(left - right) <= 1e-6 * scale


def _finding(kind: str, summary: str, evidence: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "summary": summary,
        "claim_label": "OBSERVED",
        "evidence": evidence.strip(),
    }


def _scan_equalities(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _EQ.finditer(text):
        left = _num(match.group("a")) * _num(match.group("b"))
        stated = _num(match.group("c"))
        if _close(left, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"Stated product {match.group(0)} does not equal {left:g}.",
                match.group(0),
            )
        )
    return found


def _scan_seat_sentences(text: str) -> list[dict[str, Any]]:
    rows: list[tuple[int, int, str]] = []
    for match in _SEAT.finditer(text):
        raw = match.group("seats").lower()
        seats = _WORD_NUM.get(raw)
        if seats is None and raw.isdigit():
            seats = int(raw)
        if seats is None:
            continue
        rows.append((int(match.group("n")), seats, match.group(0).strip()))
    seat_counts = {seats for _, seats, _ in rows}
    if len(seat_counts) < 2:
        return []
    bits = ", ".join(f"N={n} counts {seats}" for n, seats, _ in rows)
    evidence = " ".join(quote for _, _, quote in rows)
    return [
        _finding(
            "inconsistent_figure",
            f"Input notes mix seat assumptions ({bits}).",
            evidence,
        )
    ]


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _parse_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    index = 0
    while index < len(lines) - 1:
        header = lines[index]
        separator = lines[index + 1]
        if "|" not in header or not re.search(r"-{3,}", separator):
            index += 1
            continue
        headers = _cells(header)
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and "|" in lines[index]:
            rows.append(_cells(lines[index]))
            index += 1
        tables.append((headers, rows))
    return tables


def _header_index(headers: list[str], names: set[str]) -> int | None:
    for index, header in enumerate(headers):
        token = re.sub(r"[^a-z0-9]+", "_", header.lower()).strip("_")
        if token in names:
            return index
    return None


def _scan_tables(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for headers, rows in _parse_tables(text):
        seats_i = _header_index(headers, {"seats", "seat"})
        rate_i = _header_index(headers, {"per_seat", "rate"})
        floor_i = _header_index(headers, {"stated_floor", "floor"})
        tenants_i = _header_index(headers, {"tenants", "n"})
        if seats_i is None or rate_i is None or floor_i is None:
            continue
        mismatches: list[str] = []
        ratios: list[float] = []
        for row in rows:
            if max(seats_i, rate_i, floor_i) >= len(row):
                continue
            try:
                seats = _num(row[seats_i])
                rate = _num(row[rate_i])
                stated = _num(row[floor_i])
            except ValueError:
                continue
            if tenants_i is not None and tenants_i < len(row):
                try:
                    tenants = _num(row[tenants_i])
                except ValueError:
                    tenants = 0
                if tenants:
                    ratios.append(seats / tenants)
            if not _close(seats * rate, stated):
                mismatches.append(" | ".join(row))
        if len({round(ratio, 5) for ratio in ratios}) > 1:
            found.append(
                _finding(
                    "inconsistent_figure",
                    "Seat count per tenant is not constant across table rows.",
                    " ".join(" | ".join(row) for row in rows),
                )
            )
        if mismatches:
            found.append(
                _finding(
                    "arithmetic_error",
                    "Stated floor does not equal seats times per-seat for one or more table rows.",
                    " ".join(mismatches),
                )
            )
    return found


def _scan_option_locks(text: str) -> list[dict[str, Any]]:
    locked: dict[str, list[str]] = {}
    for match in _OPTION_AFTER.finditer(text):
        letter = match.group(1).upper()
        locked.setdefault(letter, []).append(match.group(0).strip())
    for match in _OPTION_BEFORE.finditer(text):
        letter = match.group(2).upper()
        locked.setdefault(letter, []).append(match.group(0).strip())
    found: list[dict[str, Any]] = []
    if len(locked) > 1:
        letters = " and ".join(sorted(locked))
        evidence = " ".join(
            quote for quotes in locked.values() for quote in quotes
        )
        found.append(
            _finding(
                "contradiction",
                f"Input notes lock both Option {letters}.",
                evidence,
            )
        )
    for match in _RATIONALE.finditer(text):
        left, right = match.group(1).upper(), match.group(2).upper()
        if left == right:
            continue
        found.append(
            _finding(
                "contradiction",
                f"The rationale for locked {left} describes {right}.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_rent_bands(text: str) -> list[dict[str, Any]]:
    monthly = [float(value) for value in _RENT_MO.findall(text)]
    yearly = [float(value) for value in _RENT_YR.findall(text)]
    if not monthly or not yearly:
        return []
    implied = monthly[0] * 12
    if _close(implied, yearly[0]):
        return []
    return [
        _finding(
            "inconsistent_figure",
            f"${monthly[0]:g}/sf/mo implies ${implied:g}/sf/yr, not ${yearly[0]:g}/sf/yr.",
            f"${monthly[0]:g}/sf/mo vs ${yearly[0]:g}/sf/yr",
        )
    ]


def _scan_repeated_labels(text: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[str, str]]] = {}
    for match in _LABELED_NUM.finditer(text):
        label = match.group("label").lower()
        grouped.setdefault(label, []).append((match.group("num"), match.group(0)))
    found: list[dict[str, Any]] = []
    for label, pairs in grouped.items():
        values = {pair[0] for pair in pairs}
        if len(values) < 2:
            continue
        found.append(
            _finding(
                "inconsistent_figure",
                f"Input notes give more than one value for {label}.",
                " ".join(pair[1] for pair in pairs),
            )
        )
    return found


def scan_input_notes(notes: str | None) -> dict[str, Any]:
    """Mandatory pass. Empty findings are valid. Skipping the pass is not."""
    text = notes if isinstance(notes, str) else ""
    raw: list[dict[str, Any]] = []
    raw.extend(_scan_equalities(text))
    raw.extend(_scan_seat_sentences(text))
    raw.extend(_scan_tables(text))
    raw.extend(_scan_option_locks(text))
    raw.extend(_scan_rent_bands(text))
    raw.extend(_scan_repeated_labels(text))
    findings = []
    for index, row in enumerate(raw, start=1):
        row["finding_id"] = f"in-{index}"
        findings.append(row)
    return {"checked": True, "findings": findings}


def prose_main(packet: dict[str, Any]) -> str:
    """Decision prose that must fit one page. Appendix bodies are excluded."""
    lines: list[str] = []

    def add(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            lines.append(value.strip())

    for key in (
        "opportunity_thesis",
        "completion_proof",
        "service_first_wedge",
        "affected_user",
        "economic_buyer",
        "jtbd",
        "transition_market",
        "coordination_gap",
    ):
        add(packet.get(key))
    validation = packet.get("validation_path")
    if isinstance(validation, list):
        for step in validation:
            add(step)
    buyer = packet.get("buyer_map")
    if isinstance(buyer, dict):
        for key in ("economic_buyer", "beneficiary"):
            if isinstance(buyer.get(key), str):
                lines.append(f"{key}: {buyer[key]}")
    pricing = packet.get("pricing_model")
    if isinstance(pricing, dict):
        add(pricing.get("assumptions"))
        add(pricing.get("shape"))
    risks = packet.get("risks")
    if isinstance(risks, list):
        for risk in risks:
            add(risk)
    distribution = packet.get("distribution")
    if isinstance(distribution, str):
        add(distribution)
    elif isinstance(distribution, dict):
        for value in distribution.values():
            add(value)
    handoff = packet.get("build_handoff")
    if isinstance(handoff, dict):
        add(handoff.get("summary"))
        steps = handoff.get("steps")
        if isinstance(steps, list):
            for step in steps:
                add(step)
        first = handoff.get("first_commit")
        if isinstance(first, dict):
            touch = first.get("touch")
            if isinstance(touch, list):
                for item in touch:
                    add(item)
            add(first.get("done_when"))
            add(first.get("test_to_write"))
            add(first.get("owner_role"))
    elif isinstance(handoff, str):
        add(handoff)
    kills = packet.get("kill_criteria")
    if isinstance(kills, list):
        for item in kills:
            if isinstance(item, str):
                add(item)
            elif isinstance(item, dict):
                lines.append(
                    f"{item.get('metric')} {item.get('comparison')} {item.get('threshold')} "
                    f"by {item.get('check_date')} from {item.get('data_source')}"
                )
    contradictions = packet.get("input_contradictions")
    if isinstance(contradictions, dict):
        for finding in contradictions.get("findings") or []:
            if isinstance(finding, dict):
                add(finding.get("summary"))
    research = packet.get("research")
    if isinstance(research, dict):
        for claim in research.get("observed_claims") or []:
            if isinstance(claim, dict):
                lines.append(
                    f"{claim.get('label')} {claim.get('kind')} {claim.get('url')} "
                    f"retrieved {claim.get('retrieved_at')}"
                )
    return "\n".join(lines)


def _appendix_words(appendix: dict[str, Any]) -> int:
    chunks: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            chunks.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(appendix)
    text = "\n".join(chunks)
    return len(text.split()) if text.strip() else 0


def apply_page_budget(packet: dict[str, Any]) -> dict[str, Any]:
    """Move evidence bodies into the appendix whole. Never slice strings."""
    out = dict(packet)
    appendix = dict(out.get("appendix") or {})
    research = dict(out.get("research") or {})
    claims = research.get("observed_claims") or []
    appendix_claims = [
        dict(claim)
        for claim in (appendix.get("research_claims") or [])
        if isinstance(claim, dict)
    ]
    known = {claim.get("claim_id") for claim in appendix_claims}
    slim_claims: list[dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        text = claim.get("text")
        if isinstance(text, str) and text:
            full = dict(claim)
            if full.get("claim_id") not in known:
                appendix_claims.append(full)
                known.add(full.get("claim_id"))
            slim = {key: value for key, value in claim.items() if key != "text"}
            slim["text_in"] = "appendix.research_claims"
            slim_claims.append(slim)
        else:
            slim_claims.append(dict(claim))
    research["observed_claims"] = slim_claims
    out["research"] = research

    contradictions = dict(out.get("input_contradictions") or {})
    evidence_rows = [
        dict(row)
        for row in (appendix.get("contradiction_evidence") or [])
        if isinstance(row, dict)
    ]
    known_findings = {row.get("finding_id") for row in evidence_rows}
    slim_findings: list[dict[str, Any]] = []
    for finding in contradictions.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        evidence = finding.get("evidence")
        if isinstance(evidence, str) and evidence:
            if finding.get("finding_id") not in known_findings:
                evidence_rows.append(
                    {
                        "finding_id": finding.get("finding_id"),
                        "evidence": evidence,
                    }
                )
                known_findings.add(finding.get("finding_id"))
            slim_findings.append(
                {key: value for key, value in finding.items() if key != "evidence"}
            )
        else:
            slim_findings.append(dict(finding))
    if contradictions:
        contradictions["findings"] = slim_findings
        out["input_contradictions"] = contradictions

    appendix["research_claims"] = appendix_claims
    appendix["contradiction_evidence"] = evidence_rows
    out["appendix"] = appendix

    prose = prose_main(out)
    words = len(prose.split()) if prose.strip() else 0
    chars = len(prose)
    out["page_budget"] = {
        "word_budget": WORD_BUDGET,
        "char_budget": CHAR_BUDGET,
        "main_word_count": words,
        "main_char_count": chars,
        "appendix_word_count": _appendix_words(appendix),
        "fits_one_page": words <= WORD_BUDGET and chars <= CHAR_BUDGET,
        "truncated": False,
    }
    return out


def _claim_label(obj: dict[str, Any]) -> str:
    raw = obj.get("claim_label") or obj.get("label")
    return str(raw).upper() if raw is not None else ""


def _check_observed_claim(claim: dict[str, Any], path: str, errors: list[str]) -> None:
    if _claim_label(claim) != "OBSERVED":
        return
    url = claim.get("url")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        errors.append(f"NG-RESEARCH-001: {path} OBSERVED claim missing http(s) URL")
    retrieved = claim.get("retrieved_at")
    if not isinstance(retrieved, str) or not _DATE.fullmatch(retrieved):
        errors.append(
            f"NG-RESEARCH-001: {path} OBSERVED claim missing retrieval date"
        )


def _check_kill(data: dict[str, Any], is_v12: bool, errors: list[str]) -> None:
    if "kill_criteria" not in data:
        if is_v12:
            errors.append("NG-KILL-002: schema 1.2.0 packet missing kill_criteria")
        return
    kills = data.get("kill_criteria")
    if not isinstance(kills, list):
        errors.append(
            "NG-KILL-001: kill_criteria must be a list of structured criteria, not prose"
        )
        return
    if is_v12 and not kills:
        errors.append(
            "NG-KILL-002: schema 1.2.0 packet needs at least one structured kill criterion"
        )
    for index, item in enumerate(kills):
        path = f"kill_criteria[{index}]"
        if not isinstance(item, dict):
            errors.append(f"NG-KILL-001: {path} is prose, not a structured criterion")
            continue
        for key in ("metric", "threshold", "comparison", "check_date", "data_source", "claim_label"):
            if key not in item:
                errors.append(f"NG-KILL-002: {path} missing {key}")
        metric = item.get("metric")
        if isinstance(metric, str) and not metric.strip():
            errors.append(f"NG-KILL-002: {path} metric is empty")
        threshold = item.get("threshold")
        if "threshold" in item and (
            isinstance(threshold, bool) or not isinstance(threshold, (int, float))
        ):
            errors.append(f"NG-KILL-002: {path} threshold must be a number")
        comparison = item.get("comparison")
        if "comparison" in item and comparison not in _COMPARISONS:
            errors.append(f"NG-KILL-002: {path} comparison {comparison!r} is not numeric")
        check_date = item.get("check_date")
        if isinstance(check_date, str) and not _DATE.fullmatch(check_date):
            errors.append(f"NG-KILL-002: {path} check_date must be YYYY-MM-DD")
        source = item.get("data_source")
        if isinstance(source, str) and not source.strip():
            errors.append(f"NG-KILL-002: {path} data_source is empty")
        label = _claim_label(item)
        if "claim_label" in item and label not in _LABELS:
            errors.append(f"NG-KILL-002: {path} claim_label {label!r} is unknown")
        refs = item.get("evidence_refs")
        if label == "OBSERVED" and not (isinstance(refs, list) and refs):
            errors.append(
                f"NG-KILL-003: {path} labeled OBSERVED without evidence_refs"
            )


def _check_handoff(data: dict[str, Any], is_v12: bool, errors: list[str]) -> None:
    if "build_handoff" not in data:
        if is_v12:
            errors.append("NG-HANDOFF-001: schema 1.2.0 packet missing build_handoff")
        return
    handoff = data.get("build_handoff")
    if not isinstance(handoff, dict):
        errors.append(
            "NG-HANDOFF-001: build_handoff must end with a structured first_commit"
        )
        return
    first = handoff.get("first_commit")
    if not isinstance(first, dict):
        errors.append("NG-HANDOFF-001: build_handoff missing first_commit")
        return
    touch = first.get("touch")
    if not isinstance(touch, list) or not touch or not all(
        isinstance(item, str) and item.strip() for item in touch
    ):
        errors.append("NG-HANDOFF-001: first_commit.touch needs at least one area")
    for key in ("done_when", "test_to_write", "owner_role"):
        value = first.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"NG-HANDOFF-001: first_commit.{key} is missing")


def _check_contradictions(data: dict[str, Any], is_v12: bool, errors: list[str]) -> None:
    if "input_contradictions" not in data:
        if is_v12:
            errors.append(
                "NG-INPUT-001: schema 1.2.0 packet missing input_contradictions"
            )
        return
    block = data.get("input_contradictions")
    if not isinstance(block, dict) or block.get("checked") is not True:
        errors.append("NG-INPUT-001: input contradiction pass must set checked true")
        return
    findings = block.get("findings")
    if not isinstance(findings, list):
        errors.append("NG-INPUT-001: input_contradictions.findings must be a list")
        return
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"NG-INPUT-001: findings[{index}] must be an object")
            continue
        if finding.get("kind") not in _FINDING_KINDS:
            errors.append(f"NG-INPUT-001: findings[{index}] kind is not allowed")
        summary = finding.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            errors.append(f"NG-INPUT-001: findings[{index}] summary is empty")
        if _claim_label(finding) not in _LABELS:
            errors.append(f"NG-INPUT-001: findings[{index}] claim_label is missing")


def _check_research(data: dict[str, Any], is_v12: bool, errors: list[str]) -> None:
    research = data.get("research")
    if not isinstance(research, dict):
        if is_v12:
            errors.append("NG-RESEARCH-002: schema 1.2.0 packet missing research record")
        return
    offline = research.get("offline") is True or research.get("enabled") is False
    appendix = data.get("appendix") if isinstance(data.get("appendix"), dict) else {}
    by_id: dict[Any, dict[str, Any]] = {}
    for claim in appendix.get("research_claims") or []:
        if isinstance(claim, dict) and claim.get("claim_id"):
            by_id[claim["claim_id"]] = claim
            _check_observed_claim(
                claim, f"appendix.research_claims[{claim.get('claim_id')}]", errors
            )
    for index, claim in enumerate(research.get("observed_claims") or []):
        if not isinstance(claim, dict):
            errors.append(f"NG-RESEARCH-001: observed_claims[{index}] must be an object")
            continue
        _check_observed_claim(claim, f"research.observed_claims[{index}]", errors)
        if offline and _claim_label(claim) == "OBSERVED":
            errors.append(
                "NG-RESEARCH-003: offline research record contains an OBSERVED claim"
            )
        if claim.get("text_in") == "appendix.research_claims":
            full = by_id.get(claim.get("claim_id"))
            if not isinstance(full, dict) or not str(full.get("text") or "").strip():
                errors.append(
                    f"NG-RESEARCH-001: {claim.get('claim_id')} text missing from appendix"
                )
            elif isinstance(claim.get("text"), str) and claim["text"] != full.get("text"):
                errors.append(
                    "NG-PAGE-002: research claim text on the main packet is not the full source text"
                )


def _check_page(data: dict[str, Any], is_v12: bool, errors: list[str]) -> None:
    if not is_v12:
        return
    prose = prose_main(data)
    words = len(prose.split()) if prose.strip() else 0
    chars = len(prose)
    budget = data.get("page_budget")
    if not isinstance(budget, dict):
        errors.append("NG-PAGE-001: schema 1.2.0 packet missing page_budget")
        return
    if budget.get("truncated") is not False:
        errors.append("NG-PAGE-002: main packet must not be truncated")
    fits = (
        budget.get("fits_one_page") is True
        and words <= WORD_BUDGET
        and chars <= CHAR_BUDGET
        and budget.get("main_word_count") == words
        and budget.get("main_char_count") == chars
    )
    if not fits:
        errors.append(
            f"NG-PAGE-001: main prose is {words} words / {chars} chars; "
            f"budget is {WORD_BUDGET} words / {CHAR_BUDGET} chars"
        )


def packaging_errors(data: dict[str, Any], packet_type: str) -> list[str]:
    """Bake-off checks for opportunity and commercial packets."""
    key = (packet_type or "").strip().lower().replace(" ", "_").replace("-", "_")
    if key not in {"opportunity", "commercial"}:
        return []
    if not isinstance(data, dict):
        return []
    version = data.get("schema_version")
    is_v12 = _version_ge(version, SCHEMA_VERSION)
    errors: list[str] = []
    _check_kill(data, is_v12, errors)
    _check_handoff(data, is_v12, errors)
    _check_contradictions(data, is_v12, errors)
    _check_research(data, is_v12, errors)
    _check_page(data, is_v12, errors)
    return errors


def _version_ge(version: Any, minimum: str) -> bool:
    if not isinstance(version, str):
        return False

    def parts(value: str) -> tuple[int, int, int] | None:
        bits = value.split(".")
        if len(bits) != 3:
            return None
        try:
            return int(bits[0]), int(bits[1]), int(bits[2])
        except ValueError:
            return None

    left = parts(version)
    right = parts(minimum)
    if left is None or right is None:
        return version == minimum
    return left >= right


def attach_v12(
    packet: dict[str, Any],
    *,
    notes: str,
    research_policy: dict[str, Any],
    queries: list[str],
    schema_id: str,
    handoff: dict[str, Any],
    kill_criteria: list[dict[str, Any]],
    adapter: research_mode.ResearchAdapter | None = None,
) -> dict[str, Any]:
    """Return a schema 1.2.0 packet. Does not invent buyers, revenue, or prices."""
    out = dict(packet)
    out["schema_id"] = schema_id
    out["schema_version"] = SCHEMA_VERSION
    out["input_contradictions"] = scan_input_notes(notes)
    research = research_mode.run_research(research_policy, queries, adapter=adapter)
    out["research"] = research
    if research.get("research_ran"):
        out["research_search_dag"] = research_mode.research_search_dag(
            queries, research.get("observed_claims") or []
        )
    else:
        out.pop("research_search_dag", None)
    out["build_handoff"] = handoff
    out["kill_criteria"] = list(kill_criteria)
    return apply_page_budget(out)


def seat_option_example_packet() -> dict[str, Any]:
    """Synthetic seat-floor opportunity used as the 1.2.0 sample. Fixture data only."""
    base = {
        "blocked_transition": {
            "from": "pricing notes that mix seat assumptions and option locks",
            "to": "one declared seat rule and one locked option",
        },
        "outcome_model": {
            "success": "notes reconcile to one seat rule and one option",
            "failure": "ship a price from mixed tiers",
        },
        "system_topology": {
            "actors": ["operator"],
            "systems": ["pricing notes"],
        },
        "opportunity_thesis": (
            "The fixture notes disagree with themselves. Do not invent a buyer "
            "or a price to paper over the seat table or the option lock."
        ),
        "validation_path": [
            "list contradiction findings",
            "operator picks one seat rule",
            "operator picks one locked option",
        ],
        "completion_proof": (
            "A revised note with one seat assumption per tier and one locked option, "
            "checked by re-running the input pass."
        ),
        "logic_label": "mixed",
        "scorecard": {"evidence_density": 0.5, "outcome_clarity": 0.6},
        "promotion_state": "CONCEPTUAL",
        "authority": "advisory_only",
        "grants_execution": False,
        "affected_user": "operator reconciling the fixture pricing notes",
        "economic_buyer": "NOT_COMPUTABLE_until_declared",
        "transition_market": "mixed seat table and dual option lock",
        "coordination_gap": "notes assert two seat rules and two locked options",
        "service_first_wedge": "reconcile the notes before any price is proposed",
        "distribution": "operator review of the fixture notes only",
        "failure_modes": "invented buyer, invented price, or a truncated finding",
        "jtbd": "see the contradictions before deciding",
    }
    return attach_v12(
        base,
        notes=SEAT_OPTION_NOTES,
        research_policy={
            "enabled": True,
            "offline": False,
            "adapter": "fixture",
        },
        queries=["seat floor"],
        schema_id="neon-genie/opportunity-packet",
        adapter=research_mode.FixtureAdapter([FIXTURE_SOURCE]),
        handoff={
            "summary": "Reconcile the fixture notes before any build.",
            "steps": [
                "Read the contradiction findings.",
                "Do not add a buyer or a price that the notes do not state.",
            ],
            "first_commit": {
                "touch": ["pricing table notes", "option lock decision"],
                "done_when": (
                    "One seat assumption is declared for every tier and only one option is locked."
                ),
                "test_to_write": (
                    "Re-run the input contradiction pass and expect zero seat-assumption "
                    "and option-lock findings."
                ),
                "owner_role": "operator",
            },
        },
        kill_criteria=[
            {
                "criterion_id": "kc-seat-mix",
                "metric": "tiers_with_mixed_seat_assumption",
                "threshold": 0,
                "comparison": "gt",
                "check_date": "2026-10-15",
                "data_source": "operator pricing table in the input notes",
                "claim_label": "INFERRED",
                "evidence_refs": ["operator_notes"],
                "role": "guardrail",
            }
        ],
    )


def attach_offline(
    packet: dict[str, Any],
    *,
    notes: str,
    schema_id: str,
    handoff: dict[str, Any],
    kill_criteria: list[dict[str, Any]],
) -> dict[str, Any]:
    """Packaging-recipe path. Does not call an adapter."""
    return attach_v12(
        packet,
        notes=notes,
        research_policy={"enabled": False, "offline": True},
        queries=[],
        schema_id=schema_id,
        handoff=handoff,
        kill_criteria=kill_criteria,
    )
