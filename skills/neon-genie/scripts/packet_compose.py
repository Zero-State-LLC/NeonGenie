#!/usr/bin/env python3
"""Shape opportunity and commercial packets after the bake-off rounds.

Before the packet is written:

1. Scan input notes for contradictions, arithmetic errors, and inconsistent figures.
2. Optionally gather sources (see research_mode). Offline adds no OBSERVED claims.
3. Attach structured kill criteria, recompute each threshold from its inputs,
   and attach a first-commit handoff.
4. Keep decision prose inside one page. Evidence moves intact into ``appendix``.

Schema 1.2.0 opts into the first bake-off checks. Schema 1.3.0 adds kill
recomputation. Older packets stay valid.
"""

from __future__ import annotations

import json
import re
from typing import Any

import research_mode

SCHEMA_VERSION = "1.3.0"
BAKEOFF_VERSION = "1.2.0"
WORD_BUDGET = 450
CHAR_BUDGET = 3200

_COMPARISONS = frozenset({"lt", "lte", "gt", "gte", "eq", "neq"})
_LABELS = frozenset({"OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"})
_FINDING_KINDS = frozenset(
    {"contradiction", "arithmetic_error", "inconsistent_figure"}
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_EQ = re.compile(
    r"(?P<a>\d[\d,]*(?:\.\d+)?)(?:\s*(?P<asuf>k|m|b))?\s*(?:seats?)?\s*(?:×|x|\*)\s*"
    r"\$?(?P<b>\d[\d,]*(?:\.\d+)?)(?:\s*(?P<bsuf>k|m|b))?\s*=\s*"
    r"\$?(?P<c>\d[\d,]*(?:\.\d+)?)(?:\s*(?P<csuf>k|m|b))?",
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
    r"\$(\d+(?:\.\d+)?)\s*(?:/\s*sf\s*/\s*(?:yr|year)|per\s+sf\s+per\s+year)",
    re.IGNORECASE,
)
_LABELED_NUM = re.compile(
    r"(?P<label>[a-z][a-z]+(?:\s+[a-z][a-z]+){0,4})"
    r"\s*[:=]\s*\$?(?P<num>\d[\d,]*(?:\.\d+)?)"
    r"(?:\s*(?P<suffix>k|m|b|thousand|million|billion))?",
    re.IGNORECASE,
)
_QTY_LABEL = re.compile(
    r"\b(price|floor|users|deposit|fee|cost|rate|rent|seats|tokens|count)\b",
    re.IGNORECASE,
)
_FEE_ABS = re.compile(
    r"subtotal\s+\$?(?P<base>\d[\d,]*(?:\.\d+)?)\b"
    r"[^.\n]{0,120}?\bfee\s+\$?(?P<fee>\d[\d,]*(?:\.\d+)?)\b"
    r"[^.\n]{0,80}?\b(?:total|equals)\s+\$?(?P<total>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_FEE_PCT = re.compile(
    r"\$?(?P<base>\d[\d,]*(?:\.\d+)?)\b[^.\n]{0,40}?\bplus\s+(?:a\s+)?"
    r"(?P<pct>\d+(?:\.\d+)?)%\s+fee(?:\s+and\s+\$?(?P<fixed>\d+(?:\.\d+)?))?"
    r"\s+equals\s+\$?(?P<total>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_PER_UNIT = re.compile(
    r"N\s*=\s*(?P<n>\d+)[^.\n]{0,60}?per-unit floor\s+\$?(?P<amt>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_PER_SEAT_N = re.compile(
    r"N\s*=\s*(?P<n>\d+)[^.\n]{0,40}?per[- ]seat\s+\$?(?P<amt>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_INCLUDED_AT_N = re.compile(
    r"(?P<item>(?:[A-Za-z]+(?:-[A-Za-z]+)?\s+){1,6})at\s+N\s*=\s*(?P<yes>\d+)\b"
    r"[^.\n]{0,80}?\bnot\s+at\s+N\s*=\s*(?P<rest>\d+(?:\s+or\s+N\s*=\s*\d+)*)",
    re.IGNORECASE,
)
_ALL_COUNT = re.compile(
    r"\ball\s+(?P<n>two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    re.IGNORECASE,
)
_NOT_COUNT = re.compile(
    r"\bnot\s+(?P<n>two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
    re.IGNORECASE,
)
_MONTHLY_AMOUNT = re.compile(
    r"\$?(?P<num>\d+(?:\.\d+)?)\s+(?:monthly|per month|a month)\b",
    re.IGNORECASE,
)
_YEARLY_AMOUNT = re.compile(
    r"\$?(?P<num>\d+(?:\.\d+)?)\s+(?:yearly|per year|a year)\b",
    re.IGNORECASE,
)
_OPTION_RECOMMENDED = re.compile(
    r"\boption\s+([A-Z])\b[^.\n]{0,40}?\b(?:recommended|default)\b"
    r"|\b(?:recommended|default)\b[^.\n]{0,40}?\boption\s+([A-Z])\b",
    re.IGNORECASE,
)
_OPTION_DEF = re.compile(
    r"option\s+([A-Z])\s*:\s*(?P<body>[^.\n]+)",
    re.IGNORECASE,
)
_OPTION_WHY = re.compile(
    r"rationale for (?:locking\s+)?option\s+([A-Z])\s*:\s*(?P<body>[^.\n]+)",
    re.IGNORECASE,
)
_AMOUNT = re.compile(
    r"(?<![A-Za-z0-9_])\$?(?P<num>\d[\d,]*(?:\.\d+)?)"
    r"(?:\s*(?P<suffix>k|m|b|thousand|million|billion))?\b",
    re.IGNORECASE,
)
_SUFFIX_VALUE = {
    "": 1.0,
    "k": 1_000.0,
    "thousand": 1_000.0,
    "m": 1_000_000.0,
    "million": 1_000_000.0,
    "b": 1_000_000_000.0,
    "billion": 1_000_000_000.0,
}
_STOP = frozenset(
    "the a an of to for and or is are was were with that this stays stay "
    "into from by on as at be it its".split()
)
_PLACEHOLDER_DATES = frozenset(
    {"0000-00-00", "0001-01-01", "1900-01-01", "1970-01-01", "9999-12-31"}
)
_PLACEHOLDER_WORD = re.compile(
    r"\b(placeholder|tbd|todo|unspecified|unknown)\b",
    re.IGNORECASE,
)
_QUOTE_POLARITY = {
    "negative": "neg",
    "fail": "neg",
    "failed": "neg",
    "failure": "neg",
    "failures": "neg",
    "reject": "neg",
    "rejected": "neg",
    "banned": "neg",
    "absent": "neg",
    "positive": "pos",
    "pass": "pos",
    "passed": "pos",
    "passes": "pos",
    "allowed": "pos",
    "succeed": "pos",
    "succeeded": "pos",
}
_QUOTE_NEGATORS = frozenset({"not", "no", "never", "without"})
_QUOTE_TOKEN = re.compile(r"[a-z]+n't|[a-z]+|[.!?]")
_FORMULA_REQUIRES = {
    "identity": ("value",),
    "sum": ("values",),
    "min": ("values",),
    "product": ("values",),
    "net_of_percent_and_fixed": ("amount", "percent", "fixed"),
    "min_tier_net_of_fee": ("tiers", "percent", "fixed"),
}
_DEPENDS_INPUT = {
    "value": "value",
    "values": "values",
    "amount": "amount",
    "percent": "percent",
    "fixed": "fixed",
    "tiers": "tiers",
    "stripe_percent": "percent",
    "stripe_fee": "percent",
    "stripe_fixed": "fixed",
    "every_tier": "tiers",
}
_MIN_TIER_DEPENDS = ("every_tier", "stripe_percent", "stripe_fixed")
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


def _scaled(number: str, suffix: str | None) -> float:
    key = (suffix or "").lower()
    return _num(number) * _SUFFIX_VALUE[key]


def _tokens(text: str) -> set[str]:
    return {
        tok
        for tok in re.findall(r"[a-z0-9]+", text.lower())
        if tok not in _STOP and len(tok) > 2
    }


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.])\s+|\n+", text) if part.strip()]


def _magnitudes(text: str) -> list[float]:
    found: list[float] = []
    for match in _AMOUNT.finditer(text):
        found.append(_scaled(match.group("num"), match.group("suffix")))
    return found


def date_is_placeholder(value: Any) -> bool:
    """True when a date string is a sentinel or says it is not a real date."""
    if not isinstance(value, str):
        return False
    text = value.strip().lower()
    if text in _PLACEHOLDER_DATES:
        return True
    return _PLACEHOLDER_WORD.search(text) is not None


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
        left = _scaled(match.group("a"), match.group("asuf")) * _scaled(
            match.group("b"), match.group("bsuf")
        )
        stated = _scaled(match.group("c"), match.group("csuf"))
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
    locked_letters = set(locked)
    recommended: dict[str, str] = {}
    for match in _OPTION_RECOMMENDED.finditer(text):
        letter = (match.group(1) or match.group(2) or "").upper()
        if letter:
            recommended[letter] = match.group(0).strip()
    if locked_letters:
        for letter, quote in recommended.items():
            if letter in locked_letters:
                continue
            locked_name = " and ".join(sorted(locked_letters))
            found.append(
                _finding(
                    "contradiction",
                    f"Option {locked_name} is locked and Option {letter} is still recommended.",
                    quote,
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


def _scan_period_mismatch(text: str) -> list[dict[str, Any]]:
    """Monthly and yearly statements of the same unit that do not agree."""
    found: list[dict[str, Any]] = []
    monthly = [float(value) for value in _RENT_MO.findall(text)]
    yearly = [float(value) for value in _RENT_YR.findall(text)]
    for month in monthly:
        implied = month * 12
        for year in yearly:
            if _close(implied, year):
                continue
            found.append(
                _finding(
                    "inconsistent_figure",
                    f"${month:g}/sf/mo implies ${implied:g}/sf/yr, not ${year:g}/sf/yr.",
                    f"${month:g}/sf/mo vs ${year:g}/sf/yr",
                )
            )
            return found
    month_amounts = [float(value) for value in _MONTHLY_AMOUNT.findall(text)]
    year_amounts = [float(value) for value in _YEARLY_AMOUNT.findall(text)]
    for month in month_amounts:
        implied = month * 12
        for year in year_amounts:
            if _close(implied, year):
                continue
            found.append(
                _finding(
                    "inconsistent_figure",
                    f"${month:g} monthly implies ${implied:g} yearly, not ${year:g} yearly.",
                    f"${month:g} monthly vs ${year:g} yearly",
                )
            )
            return found
    return found


def _scan_repeated_labels(text: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[tuple[float, str]]] = {}
    for match in _LABELED_NUM.finditer(text):
        label = re.sub(r"\s+", " ", match.group("label").lower()).strip()
        if _QTY_LABEL.search(label) is None:
            continue
        amount = _scaled(match.group("num"), match.group("suffix"))
        grouped.setdefault(label, []).append((amount, match.group(0)))
    found: list[dict[str, Any]] = []
    for label, pairs in grouped.items():
        unique: list[float] = []
        for value, _quote in pairs:
            if any(_close(value, seen) for seen in unique):
                continue
            unique.append(value)
        if len(unique) < 2:
            continue
        found.append(
            _finding(
                "inconsistent_figure",
                f"Input notes give more than one value for {label}.",
                " ".join(pair[1] for pair in pairs),
            )
        )
    return found


def _scan_fee_totals(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _FEE_ABS.finditer(text):
        base = _num(match.group("base"))
        fee = _num(match.group("fee"))
        stated = _num(match.group("total"))
        computed = base + fee
        if _close(computed, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"Fee-inclusive total {stated:g} does not equal {base:g} + {fee:g}.",
                match.group(0).strip(),
            )
        )
    for match in _FEE_PCT.finditer(text):
        base = _num(match.group("base"))
        percent = _num(match.group("pct")) / 100.0
        fixed = _num(match.group("fixed")) if match.group("fixed") else 0.0
        stated = _num(match.group("total"))
        computed = base * (1.0 + percent) + fixed
        if _close(computed, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"Fee-inclusive total {stated:g} does not equal {computed:g} after the stated fee.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_per_unit_floors(text: str) -> list[dict[str, Any]]:
    flat = re.search(
        r"\b(flat|same|constant)\b[^.\n]{0,40}?per-unit|per-unit[^.\n]{0,40}?\b(flat|same|constant)\b",
        text,
        re.IGNORECASE,
    )
    rows: list[tuple[str, float, str]] = []
    for match in _PER_UNIT.finditer(text):
        rows.append((match.group("n"), _num(match.group("amt")), match.group(0).strip()))
    if flat and len({round(amt, 5) for _, amt, _ in rows}) > 1:
        return [
            _finding(
                "inconsistent_figure",
                "Notes call the per-unit floor flat, but the stated floors differ by N.",
                " ".join(quote for _, _, quote in rows),
            )
        ]
    same_rate = re.search(
        r"\b(same|one|constant)\b[^.\n]{0,40}?per[- ]seat",
        text,
        re.IGNORECASE,
    )
    rates: list[tuple[str, float, str]] = []
    for match in _PER_SEAT_N.finditer(text):
        rates.append((match.group("n"), _num(match.group("amt")), match.group(0).strip()))
    if same_rate and len({round(amt, 5) for _, amt, _ in rates}) > 1:
        return [
            _finding(
                "inconsistent_figure",
                "Notes call the per-seat rate the same, but the stated rates differ by N.",
                " ".join(quote for _, _, quote in rates),
            )
        ]
    return []


def _scan_included_at_n(text: str) -> list[dict[str, Any]]:
    """Same item counted at one N and omitted at another."""
    found: list[dict[str, Any]] = []
    for match in _INCLUDED_AT_N.finditer(text):
        included = match.group("yes")
        excluded = re.findall(r"\d+", match.group("rest"))
        if not excluded:
            continue
        item = re.sub(r"\s+", " ", match.group("item")).strip()
        found.append(
            _finding(
                "inconsistent_figure",
                (
                    f"{item} is included at N={included} and omitted at N="
                    + ", ".join(excluded)
                    + "."
                ),
                match.group(0).strip(),
            )
        )
    return found


def _count_word(token: str) -> str:
    return token.lower()


def _scan_count_clash(text: str) -> list[dict[str, Any]]:
    """The same count is both 'all N' and 'not N'."""
    all_hits = [( _count_word(m.group("n")), m) for m in _ALL_COUNT.finditer(text)]
    not_hits = [( _count_word(m.group("n")), m) for m in _NOT_COUNT.finditer(text)]
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for number, left in all_hits:
        for other, right in not_hits:
            if number != other or number in seen:
                continue
            seen.add(number)
            start = min(left.start(), right.start())
            end = max(left.end(), right.end())
            window = text[max(0, start - 48) : min(len(text), end + 48)]
            found.append(
                _finding(
                    "contradiction",
                    f"The same count is stated as all {number} and as not {number}. {window.strip()}",
                    window.strip(),
                )
            )
    return found


def _scan_option_overlap(text: str) -> list[dict[str, Any]]:
    definitions: dict[str, str] = {}
    rationales: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        why = _OPTION_WHY.search(line)
        if why:
            rationales.append(
                (why.group(1).upper(), why.group("body").strip(), line.strip())
            )
            continue
        for match in _OPTION_DEF.finditer(line):
            definitions[match.group(1).upper()] = match.group("body").strip()
    found: list[dict[str, Any]] = []
    for letter, body, quote in rationales:
        rationale_tokens = _tokens(body)
        if len(rationale_tokens) < 2 or letter not in definitions:
            continue
        scores: dict[str, int] = {}
        for option, definition in definitions.items():
            scores[option] = len(rationale_tokens & _tokens(definition))
        own = scores.get(letter, 0)
        others = {option: score for option, score in scores.items() if option != letter}
        if not others:
            continue
        best = max(others, key=lambda option: others[option])
        if others[best] >= 2 and others[best] > own:
            found.append(
                _finding(
                    "contradiction",
                    f"The rationale for Option {letter} describes Option {best}.",
                    quote,
                )
            )
    return found


def _shares_topic(left: str, right: str) -> bool:
    left_nums = {_scaled_key(value) for value in _magnitudes(left)}
    right_nums = {_scaled_key(value) for value in _magnitudes(right)}
    if left_nums and right_nums and left_nums & right_nums:
        return True
    return len(_tokens(left) & _tokens(right)) >= 2


def _scaled_key(value: float) -> str:
    return f"{value:.6g}"


def _scan_verification_clash(text: str) -> list[dict[str, Any]]:
    sentences = _sentences(text)
    both = [
        row
        for row in sentences
        if re.search(r"\bunverified\b", row, re.I) and re.search(r"\bverified\b", row, re.I)
    ]
    if both:
        return [
            _finding(
                "contradiction",
                "The same figure is marked both UNVERIFIED and verified.",
                both[0],
            )
        ]
    unverified = [row for row in sentences if re.search(r"\bunverified\b", row, re.I)]
    verified = [
        row
        for row in sentences
        if re.search(r"\bverified\b", row, re.I) and not re.search(r"\bunverified\b", row, re.I)
    ]
    for left in unverified:
        for right in verified:
            if not _shares_topic(left, right):
                continue
            return [
                _finding(
                    "contradiction",
                    "The same figure is marked both UNVERIFIED and verified.",
                    f"{left} {right}",
                )
            ]
    return []


_SERIES_POINT = re.compile(
    r"(?P<n>\d+)\s*(?:tenants?|units?|seats?|stalls?|booths?)?\s*:\s*"
    r"(?P<amts>\$\d[\d,]*(?:\.\d+)?(?:\s*/\s*\$?\d[\d,]*(?:\.\d+)?)*)",
    re.IGNORECASE,
)
_SUM_EQ = re.compile(
    r"(?P<body>(?:\$?\d[\d,]*(?:\.\d+)?\s*\+\s*){1,8}"
    r"\$?\d[\d,]*(?:\.\d+)?)\s*=\s*\$?(?P<total>\d[\d,]*(?:\.\d+)?)"
)
_PCT_OF = re.compile(
    r"(?P<pct>\d+(?:\.\d+)?)\s*%\s+of\s+\$?(?P<base>\d[\d,]*(?:\.\d+)?)"
    r"\s+(?:is|equals|=)\s+\$?(?P<got>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_UNIT_TOTAL = re.compile(
    r"(?P<n>\d+)\s+[A-Za-z]{3,}\s+at\s+\$?(?P<rate>\d[\d,]*(?:\.\d+)?)"
    r"\s+(?:totals?|equals|=)\s+\$?(?P<total>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_FROM_TO = re.compile(
    r"\bfrom\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\b",
    re.IGNORECASE,
)
_DOUBLED = re.compile(
    r"=\s*\$?(?P<base>\d[\d,]*(?:\.\d+)?)\b"
    r"[^.\n]{0,48}?\bx\s*2\s*=\s*\$?(?P<result>\d[\d,]*(?:\.\d+)?)",
    re.IGNORECASE,
)
_MAG_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_])(?P<num>\d[\d,]*(?:\.\d+)?)"
    r"(?:\s*(?P<suf>k|m|b|thousand|million|billion))?\b",
    re.IGNORECASE,
)
_DIRECTIVE = re.compile(
    r"\b(force|must|defaults?)\b([^.\n]{0,100})",
    re.IGNORECASE,
)
_ACTION_STOP = frozenset(
    "not the and for with this that from into only your are was has have "
    "will than then when if high low more must force default defaults "
    "defaulted unclear".split()
)


def _series_clusters(text: str) -> list[tuple[str, list[tuple[int, list[float]]]]]:
    matches = list(_SERIES_POINT.finditer(text))
    clusters: list[list[re.Match[str]]] = []
    for match in matches:
        if clusters and match.start() - clusters[-1][-1].end() <= 80:
            clusters[-1].append(match)
        else:
            clusters.append([match])
    grouped: list[tuple[str, list[tuple[int, list[float]]]]] = []
    for group in clusters:
        if len(group) < 3:
            continue
        points: list[tuple[int, list[float]]] = []
        for match in group:
            amounts = [_num(piece) for piece in re.findall(r"\d[\d,]*(?:\.\d+)?", match.group("amts"))]
            points.append((int(match.group("n")), amounts))
        quote = text[group[0].start() : group[-1].end()]
        grouped.append((quote, points))
    return grouped


def _series_residual(
    points: list[tuple[int, float]],
) -> tuple[int, float, float] | None:
    ordered = sorted({n: value for n, value in points}.items())
    if len(ordered) < 3:
        return None
    (n_lo, v_lo), (n_hi, v_hi) = ordered[-2], ordered[-1]
    denom = (1.0 / n_lo) - (1.0 / n_hi)
    if abs(denom) < 1e-12:
        return None
    shared = (v_lo - v_hi) / denom
    variable = v_hi - shared / n_hi
    for count, stated in ordered[:-2]:
        predicted = variable + shared / count
        tolerance = max(2.0, 0.05 * max(abs(predicted), abs(stated), 1.0))
        if abs(predicted - stated) > tolerance:
            return (count, stated, predicted)
    return None


def _scan_count_series(text: str) -> list[dict[str, Any]]:
    """A count series that is not the line implied by its largest counts."""
    found: list[dict[str, Any]] = []
    for quote, points in _series_clusters(text):
        width = max(len(amounts) for _, amounts in points)
        for column in range(width):
            column_points = [
                (count, amounts[column])
                for count, amounts in points
                if column < len(amounts)
            ]
            miss = _series_residual(column_points)
            if miss is None:
                continue
            count, stated, predicted = miss
            found.append(
                _finding(
                    "inconsistent_figure",
                    (
                        f"Count {count} states {stated:g}, but the larger counts "
                        f"imply {predicted:g}."
                    ),
                    quote,
                )
            )
            break
    return found


def _scan_price_below_floor(text: str) -> list[dict[str, Any]]:
    """A list price under the floor at the count the note says to use."""
    if not re.search(r"\bfail closed\b|\bmust clear\b", text, re.IGNORECASE):
        return []
    count_match = re.search(r"price as N\s*=\s*(\d+)", text, re.IGNORECASE)
    if count_match is None:
        return []
    count = int(count_match.group(1))
    floors: list[float] = []
    for _quote, points in _series_clusters(text):
        for n, amounts in points:
            if n == count and amounts:
                floors.append(max(amounts))
    if not floors:
        return []
    floor = max(floors)
    found: list[dict[str, Any]] = []
    for match in re.finditer(r"\blist\b([^.\n]{0,80})", text, re.IGNORECASE):
        for token in re.findall(r"\$(\d[\d,]*)", match.group(1)):
            price = _num(token)
            if price + 0.01 >= floor:
                continue
            found.append(
                _finding(
                    "inconsistent_figure",
                    f"List price {price:g} is below the count-{count} floor {floor:g}.",
                    match.group(0).strip(),
                )
            )
    return found


def _scan_sums(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _SUM_EQ.finditer(text):
        parts = [_num(piece) for piece in re.findall(r"\d[\d,]*(?:\.\d+)?", match.group("body"))]
        stated = _num(match.group("total"))
        total = sum(parts)
        if _close(total, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"Stated sum {stated:g} does not equal {' + '.join(f'{part:g}' for part in parts)} = {total:g}.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_percent_of(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _PCT_OF.finditer(text):
        base = _num(match.group("base"))
        percent = _num(match.group("pct"))
        stated = _num(match.group("got"))
        computed = base * percent / 100.0
        if _close(computed, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"{percent:g}% of {base:g} is {computed:g}, not {stated:g}.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_unit_totals(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _UNIT_TOTAL.finditer(text):
        count = _num(match.group("n"))
        rate = _num(match.group("rate"))
        stated = _num(match.group("total"))
        computed = count * rate
        if _close(computed, stated):
            continue
        found.append(
            _finding(
                "arithmetic_error",
                f"{count:g} at {rate:g} is {computed:g}, not {stated:g}.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_date_order(text: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for match in _FROM_TO.finditer(text):
        start, end = match.group(1), match.group(2)
        if end >= start:
            continue
        found.append(
            _finding(
                "contradiction",
                f"The interval ends on {end} before it starts on {start}.",
                match.group(0).strip(),
            )
        )
    return found


def _scan_doubled_unused(text: str) -> list[dict[str, Any]]:
    """A computed double that no later total uses."""
    found: list[dict[str, Any]] = []
    for match in _DOUBLED.finditer(text):
        base = _num(match.group("base"))
        result = _num(match.group("result"))
        if not _close(result, base * 2):
            found.append(
                _finding(
                    "arithmetic_error",
                    f"Double of {base:g} is {base * 2:g}, not {result:g}.",
                    match.group(0).strip(),
                )
            )
            continue
        later = text[match.end() :]
        later_amounts = {_num(token) for token in re.findall(r"\$(\d[\d,]*(?:\.\d+)?)", later)}
        if not later_amounts or any(_close(result, amount) for amount in later_amounts):
            continue
        found.append(
            _finding(
                "inconsistent_figure",
                f"Computed {result:g} does not appear in a later total.",
                match.group(0).strip(),
            )
        )
    return found


def _magnitude_key(match: re.Match[str]) -> str | None:
    suffix = (match.group("suf") or "").lower()
    if suffix in {"m", "million"}:
        suffix = "m"
    elif suffix in {"b", "billion"}:
        suffix = "b"
    elif suffix in {"k", "thousand"}:
        suffix = "k"
    number = match.group("num").replace(",", "")
    if not suffix and re.fullmatch(r"(?:19|20)\d{2}", number):
        return None
    value = _scaled(number, suffix or None)
    if not suffix and value < 100:
        return None
    return f"{number}{suffix}"


def _scan_label_clash(text: str) -> list[dict[str, Any]]:
    """The same magnitude is both unestablished and established."""
    negative = re.compile(r"\bunverified\b", re.IGNORECASE)
    positive = re.compile(r"\b(?:observed|verified)\b", re.IGNORECASE)
    by_key: dict[str, dict[str, str]] = {}
    for sentence in _sentences(text):
        if negative.search(sentence) and positive.search(sentence):
            pole = "both"
        elif negative.search(sentence):
            pole = "neg"
        elif positive.search(sentence):
            pole = "pos"
        else:
            continue
        for match in _MAG_TOKEN.finditer(sentence):
            key = _magnitude_key(match)
            if key is None:
                continue
            slot = by_key.setdefault(key, {})
            slot.setdefault(pole, sentence)
    found: list[dict[str, Any]] = []
    for slot in by_key.values():
        if "both" in slot or ("neg" in slot and "pos" in slot):
            evidence = " ".join(slot[name] for name in ("neg", "pos", "both") if name in slot)
            found.append(
                _finding(
                    "contradiction",
                    "The same quantity is marked both UNVERIFIED and OBSERVED.",
                    evidence,
                )
            )
    return found


def _scan_directive_clash(text: str) -> list[dict[str, Any]]:
    """An action is both forced and excluded."""
    positive: dict[str, str] = {}
    negative: dict[str, str] = {}
    for match in _DIRECTIVE.finditer(text):
        keyword = match.group(1).lower()
        clause = match.group(2)
        quote = (match.group(1) + clause).strip()
        neg = re.search(r"\bnot\s+`?([A-Za-z_][A-Za-z0-9_]{2,})`?", clause)
        if neg:
            negative.setdefault(neg.group(1).lower(), quote)
        head = re.split(r"\bnot\b", clause, maxsplit=1, flags=re.IGNORECASE)[0]
        if re.match(r"\s*not\b", clause, re.IGNORECASE):
            continue
        if keyword.startswith("default"):
            assigned = re.search(r"=\s*`?([A-Za-z_][A-Za-z0-9_]{2,})`?", head)
            if assigned:
                positive.setdefault(assigned.group(1).lower(), quote)
            continue
        for token in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`|\b([A-Za-z]+_[A-Za-z0-9_]+)\b", head):
            word = (token[0] or token[1]).lower()
            if word not in _ACTION_STOP:
                positive.setdefault(word, quote)
        plain = [
            word.lower()
            for word in re.findall(r"\b([A-Za-z][a-z]{3,20})\b", head)
            if word.lower() not in _ACTION_STOP
        ]
        if len(plain) == 1 and len(head) < 48:
            positive.setdefault(plain[0], quote)
    found: list[dict[str, Any]] = []
    for word, quote in positive.items():
        if word not in negative:
            continue
        found.append(
            _finding(
                "contradiction",
                f"The action {word} is both required and excluded.",
                f"{quote} {negative[word]}",
            )
        )
    return found


def _scan_label_scope(text: str) -> list[dict[str, Any]]:
    """A number from an OBSERVED section that also says unverified is reused as fact."""
    chunks = re.split(r"(?m)^(#{1,6}[^\n]*)$", text)
    found: list[dict[str, Any]] = []
    index = 1
    while index + 1 < len(chunks):
        heading, body = chunks[index], chunks[index + 1]
        index += 2
        if not re.search(r"\bOBSERVED\b", heading):
            continue
        if not re.search(r"\bunverified\b", body, re.IGNORECASE):
            continue
        ranges = []
        for token in re.findall(r"\d{2,}\s*-\s*\d{2,}", body):
            sides = [int(piece) for piece in re.split(r"\s*-\s*", token)]
            if len(sides) != 2 or sides[0] >= 1900 or sides[1] >= 1900:
                continue
            ranges.append(token)
        if not ranges:
            continue
        rest_at = text.find(body) + len(body)
        rest = text[rest_at:]
        unverified_line = ""
        for line in body.splitlines():
            if re.search(r"\bunverified\b", line, re.IGNORECASE):
                unverified_line = line.strip()
                break
        for token in ranges:
            compact = re.sub(r"\s+", "", token)
            for sentence in _sentences(rest):
                if compact not in re.sub(r"\s+", "", sentence):
                    continue
                if re.search(
                    r"\bunverified\b|\bnot_computable\b|\bspeculative\b|\binferred\b",
                    sentence,
                    re.IGNORECASE,
                ):
                    continue
                found.append(
                    _finding(
                        "contradiction",
                        "A figure from a section labeled OBSERVED that also says unverified is reused as fact.",
                        f"{heading.strip()} {unverified_line} {sentence.strip()}",
                    )
                )
                break
    return found


def _option_letter(cell: str) -> str | None:
    raw = re.sub(r"[*_`]", "", cell).strip()
    match = re.match(r"([A-Z])\b", raw)
    return match.group(1) if match else None


def _pole(text: str) -> str | None:
    high = re.search(r"\b(highest|high|maximizes|maximize|maximum|most)\b", text, re.IGNORECASE)
    low = re.search(r"\b(lowest|low|minimizes|minimize|minimum|least)\b", text, re.IGNORECASE)
    if high and not low:
        return "high"
    if low and not high:
        return "low"
    return None


def _scan_option_polarity(text: str) -> list[dict[str, Any]]:
    """A rationale's attribute polarity matches a different option than the lock."""
    tables = _parse_tables(text)
    found: list[dict[str, Any]] = []
    for match in re.finditer(r"rationale\b(.{0,300})", text, re.IGNORECASE):
        rationale = match.group(1)
        prior = text[: match.start()]
        locks = list(
            re.finditer(
                r"option\s+([A-Z])\b[^.\n]{0,40}?\b(?:locked|selected|chosen)\b"
                r"|\b(?:locked|selected|chosen)\b[^.\n]{0,60}?\boption\s+([A-Z])\b",
                prior,
                re.IGNORECASE,
            )
        )
        if not locks:
            continue
        last = locks[-1]
        locked = (last.group(1) or last.group(2) or "").upper()
        if not locked:
            continue
        for headers, rows in tables:
            option_i = _header_index(headers, {"option", "options"})
            if option_i is None:
                continue
            letters: dict[str, list[str]] = {}
            for row in rows:
                if option_i >= len(row):
                    continue
                letter = _option_letter(row[option_i])
                if letter:
                    letters[letter] = row
            if locked not in letters:
                continue
            for col, header in enumerate(headers):
                if col == option_i:
                    continue
                words = [
                    word.lower()
                    for word in re.findall(r"[A-Za-z]{5,}", header)
                    if word.lower() not in {"option", "structure", "buyer"}
                ]
                for word in words:
                    if word not in rationale.lower():
                        continue
                    at = rationale.lower().find(word)
                    reason_pole = _pole(rationale[max(0, at - 40) : at + len(word)])
                    if reason_pole is None:
                        continue
                    own = _pole(letters[locked][col]) if col < len(letters[locked]) else None
                    if own == reason_pole:
                        continue
                    other = None
                    for letter, row in letters.items():
                        if letter == locked or col >= len(row):
                            continue
                        if _pole(row[col]) == reason_pole:
                            other = letter
                            break
                    if other is None:
                        continue
                    found.append(
                        _finding(
                            "contradiction",
                            (
                                f"The rationale for locked Option {locked} agrees with "
                                f"Option {other}."
                            ),
                            match.group(0).strip(),
                        )
                    )
                    return found
    return found


def _scan_credit_periods(text: str) -> list[dict[str, Any]]:
    """One credit against monthly amounts that imply very different durations."""
    found: list[dict[str, Any]] = []
    seen: set[tuple[float, float, float]] = set()
    for match in re.finditer(r"\bcredits?\b", text, re.IGNORECASE):
        window = text[max(0, match.start() - 500) : match.end() + 900]
        monthly_at = re.search(r"\bmonthly\b", window, re.IGNORECASE)
        if monthly_at is None:
            continue
        span = window[monthly_at.start() : monthly_at.end() + 220]
        monthly = [
            _num(token)
            for token in re.findall(r"\$(\d[\d,]*(?:\.\d+)?)", span)
        ]
        monthly = [value for value in monthly if value > 0]
        if len(set(round(value, 2) for value in monthly)) < 2:
            continue
        lump_zone = window[: monthly_at.start()] + window[monthly_at.end() + 220 :]
        lumps = []
        for anchor in re.finditer(
            r"\b(?:prepay|contribution|stipend|credits?)\b",
            lump_zone,
            re.IGNORECASE,
        ):
            nearby = lump_zone[max(0, anchor.start() - 40) : anchor.end() + 40]
            lumps.extend(_num(token) for token in re.findall(r"\$(\d[\d,]*(?:\.\d+)?)", nearby))
        if not lumps:
            continue
        lump = max(lumps)
        low, high = min(monthly), max(monthly)
        if low <= 0 or high / low < 2:
            continue
        key = (round(lump, 2), round(low, 2), round(high, 2))
        if key in seen:
            continue
        seen.add(key)
        found.append(
            _finding(
                "inconsistent_figure",
                (
                    f"The same credit of {lump:g} covers {lump / high:g} months "
                    f"at one monthly amount and {lump / low:g} months at another."
                ),
                " ".join(window.split())[:1500],
            )
        )
    return found


def scan_input_notes(notes: str | None) -> dict[str, Any]:
    """Mandatory pass. Empty findings are valid. Skipping the pass is not."""
    text = notes if isinstance(notes, str) else ""
    raw: list[dict[str, Any]] = []
    raw.extend(_scan_equalities(text))
    raw.extend(_scan_sums(text))
    raw.extend(_scan_percent_of(text))
    raw.extend(_scan_unit_totals(text))
    raw.extend(_scan_fee_totals(text))
    raw.extend(_scan_seat_sentences(text))
    raw.extend(_scan_included_at_n(text))
    raw.extend(_scan_per_unit_floors(text))
    raw.extend(_scan_tables(text))
    raw.extend(_scan_count_series(text))
    raw.extend(_scan_price_below_floor(text))
    raw.extend(_scan_doubled_unused(text))
    raw.extend(_scan_option_locks(text))
    raw.extend(_scan_option_overlap(text))
    raw.extend(_scan_option_polarity(text))
    raw.extend(_scan_period_mismatch(text))
    raw.extend(_scan_credit_periods(text))
    raw.extend(_scan_repeated_labels(text))
    raw.extend(_scan_verification_clash(text))
    raw.extend(_scan_label_clash(text))
    raw.extend(_scan_label_scope(text))
    raw.extend(_scan_directive_clash(text))
    raw.extend(_scan_count_clash(text))
    raw.extend(_scan_date_order(text))
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


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _as_floats(value: Any) -> list[float] | None:
    if not isinstance(value, list) or not value:
        return None
    out: list[float] = []
    for item in value:
        number = _as_float(item)
        if number is None:
            return None
        out.append(number)
    return out


def _flip_polarity(label: str) -> str:
    return "pos" if label == "neg" else "neg"


def _polarity(text: str) -> set[str]:
    """Polarity words, with not/no/never/without/n't flipping the next one.

    Negation lasts for a few tokens and dies at sentence punctuation, so a
    later sentence is not flipped by an earlier "not".
    """
    found: set[str] = set()
    pending = 0
    for token in _QUOTE_TOKEN.findall(text.lower()):
        if token in ".!?":
            pending = 0
            continue
        if token.endswith("n't") or token in _QUOTE_NEGATORS:
            pending = 6
            continue
        if token in _QUOTE_POLARITY:
            label = _QUOTE_POLARITY[token]
            if pending:
                label = _flip_polarity(label)
                pending = 0
            found.add(label)
            continue
        if pending:
            pending -= 1
    return found


def quote_support(claim: str, quote: str) -> str:
    """Return supports, contradicts, or inconclusive. Deterministic only."""
    if not isinstance(claim, str) or not isinstance(quote, str):
        return "inconclusive"
    if not claim.strip() or not quote.strip():
        return "inconclusive"
    claim_nums = _magnitudes(claim)
    quote_nums = _magnitudes(quote)
    for number in claim_nums:
        if not any(_close(number, other) for other in quote_nums):
            return "contradicts"
    claim_pol = _polarity(claim)
    quote_pol = _polarity(quote)
    if claim_pol and not quote_pol:
        return "contradicts"
    if claim_pol and quote_pol and claim_pol.isdisjoint(quote_pol):
        return "contradicts"
    if claim_pol and claim_pol <= quote_pol:
        return "supports"
    if claim_nums and not claim_pol:
        return "supports"
    return "inconclusive"


def recompute_kill_threshold(item: dict[str, Any]) -> tuple[float | None, list[str]]:
    """Recompute a kill threshold from derivation inputs. Missing inputs fail closed."""
    derivation = item.get("derivation")
    if not isinstance(derivation, dict):
        return None, ["missing derivation"]
    formula = derivation.get("formula")
    inputs = derivation.get("inputs")
    if formula not in _FORMULA_REQUIRES:
        return None, [f"unknown formula {formula!r}"]
    if not isinstance(inputs, dict):
        return None, ["missing inputs"]
    problems: list[str] = []
    depends = derivation.get("depends_on")
    if not isinstance(depends, list) or not depends:
        problems.append("missing depends_on")
        depends = []
    needed = list(_FORMULA_REQUIRES[str(formula)])
    for name in depends:
        key = _DEPENDS_INPUT.get(str(name))
        if key is None:
            problems.append(f"unknown dependency {name}")
            continue
        if key not in needed:
            needed.append(key)
        if inputs.get(key) is None:
            problems.append(f"missing input for {name}")
    for key in _FORMULA_REQUIRES[str(formula)]:
        if inputs.get(key) is None:
            problems.append(f"missing input {key}")
    if formula == "min_tier_net_of_fee":
        declared = {str(name) for name in depends}
        for name in _MIN_TIER_DEPENDS:
            if name not in declared:
                problems.append(f"missing depends_on {name}")
    if problems:
        return None, problems
    if formula == "identity":
        value = _as_float(inputs.get("value"))
        if value is None:
            return None, ["value must be numeric"]
        return value, []
    if formula in {"sum", "min", "product"}:
        values = _as_floats(inputs.get("values"))
        if values is None:
            return None, ["values must be a non-empty numeric list"]
        if formula == "sum":
            return sum(values), []
        if formula == "min":
            return min(values), []
        product = 1.0
        for number in values:
            product *= number
        return product, []
    if formula == "net_of_percent_and_fixed":
        amount = _as_float(inputs.get("amount"))
        percent = _as_float(inputs.get("percent"))
        fixed = _as_float(inputs.get("fixed"))
        if amount is None or percent is None or fixed is None:
            return None, ["amount, percent, and fixed must be numeric"]
        return amount * (1.0 - percent) - fixed, []
    tiers = _as_floats(inputs.get("tiers"))
    percent = _as_float(inputs.get("percent"))
    fixed = _as_float(inputs.get("fixed"))
    if tiers is None or percent is None or fixed is None:
        return None, ["tiers, percent, and fixed must be numeric"]
    tier_count = inputs.get("tier_count", derivation.get("tier_count"))
    if isinstance(tier_count, bool) or not isinstance(tier_count, (int, float)):
        return None, ["tier_count is required so every tier is present"]
    if len(tiers) != int(tier_count):
        return None, [f"tiers has {len(tiers)} values; tier_count is {int(tier_count)}"]
    return min(tiers) * (1.0 - percent) - fixed, []


def identity_derivation(value: int | float) -> dict[str, Any]:
    """Threshold that is exactly the stated test count. Not an observed price."""
    return {
        "formula": "identity",
        "inputs": {"value": value},
        "depends_on": ["value"],
    }


_COST_METRIC = re.compile(r"cost|price|usd|fee|rent|subsidy|tier", re.IGNORECASE)
_TIER_PAIR = re.compile(
    r"\$?(?P<a>\d{2,7}(?:\.\d+)?)\s+and\s+\$?(?P<b>\d{2,7}(?:\.\d+)?)\s+tiers?\b",
    re.IGNORECASE,
)
_COST_WORD = r"(?:stripe|card|fee)"
_COST_FEE_PCT = re.compile(
    rf"\b{_COST_WORD}\b[^.\n]{{0,48}}?(?P<pct>\d+(?:\.\d+)?)\s*%"
    rf"|(?P<pct2>\d+(?:\.\d+)?)\s*%[^.\n]{{0,48}}?\b{_COST_WORD}\b",
    re.IGNORECASE,
)
_COST_FEE_FIXED = re.compile(
    rf"\b{_COST_WORD}\b[^.\n]{{0,48}}?\$?(?P<fixed>\d+\.\d{{2}})"
    rf"|\$?(?P<fixed2>\d+\.\d{{2}})[^.\n]{{0,24}}?\b{_COST_WORD}\b",
    re.IGNORECASE,
)


def _cost_bearing(item: dict[str, Any]) -> bool:
    metric = str(item.get("metric") or "")
    if _COST_METRIC.search(metric):
        return True
    derivation = item.get("derivation")
    formula = derivation.get("formula") if isinstance(derivation, dict) else None
    return formula in {"min_tier_net_of_fee", "net_of_percent_and_fixed"}


def _as_percent(raw: str) -> float:
    value = float(raw)
    if value > 1:
        return value / 100.0
    return value


def declared_cost_inputs(text: str) -> dict[str, list[float]]:
    """Price tiers and card fees stated in packet text. Not a price invention."""
    tiers: list[float] = []
    percents: list[float] = []
    fixed: list[float] = []

    def add(bucket: list[float], value: float) -> None:
        if any(_close(value, seen) for seen in bucket):
            return
        bucket.append(value)

    for match in _TIER_PAIR.finditer(text):
        add(tiers, _num(match.group("a")))
        add(tiers, _num(match.group("b")))
    for match in _COST_FEE_PCT.finditer(text):
        raw = match.group("pct") or match.group("pct2")
        if raw:
            add(percents, _as_percent(raw))
    for match in _COST_FEE_FIXED.finditer(text):
        raw = match.group("fixed") or match.group("fixed2")
        if raw:
            add(fixed, _num(raw))
    return {"tiers": tiers, "percents": percents, "fixed": fixed}


def _packet_text_without_derivation(packet: dict[str, Any], index: int) -> str:
    clone = json.loads(json.dumps(packet))
    kills = clone.get("kill_criteria")
    if isinstance(kills, list) and 0 <= index < len(kills) and isinstance(kills[index], dict):
        kills[index].pop("derivation", None)
    return json.dumps(clone)


def _input_has(inputs: dict[str, Any], key: str, value: float) -> bool:
    raw = inputs.get(key)
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return False
    return _close(float(raw), value)


def _tiers_have(inputs: dict[str, Any], value: float) -> bool:
    tiers = inputs.get("tiers")
    if not isinstance(tiers, list):
        return False
    for item in tiers:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            continue
        if _close(float(item), value):
            return True
    return False


def ignored_cost_inputs(item: dict[str, Any], packet: dict[str, Any], index: int) -> list[str]:
    """Cost inputs stated elsewhere in the packet and absent from this derivation."""
    if not _cost_bearing(item):
        return []
    derivation = item.get("derivation")
    if not isinstance(derivation, dict):
        return []
    formula = derivation.get("formula")
    inputs = derivation.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
    if formula == "identity":
        justification = derivation.get("justification")
        if isinstance(justification, str) and justification.strip():
            return []
    registry = declared_cost_inputs(_packet_text_without_derivation(packet, index))
    missing: list[str] = []
    for tier in registry["tiers"]:
        if not _tiers_have(inputs, tier):
            missing.append(f"tier {tier:g}")
    for percent in registry["percents"]:
        if not _input_has(inputs, "percent", percent):
            missing.append(f"percent {percent:g}")
    for fee in registry["fixed"]:
        if not _input_has(inputs, "fixed", fee):
            missing.append(f"fixed {fee:g}")
    return missing


def _check_quote(
    claim: dict[str, Any],
    path: str,
    errors: list[str],
    quote_judge: Any,
) -> None:
    quote = claim.get("quote")
    if not isinstance(quote, str) or not quote.strip():
        return
    text = claim.get("text") or claim.get("claim") or ""
    if not isinstance(text, str):
        text = ""
    verdict = quote_support(text, quote)
    if verdict == "inconclusive" and quote_judge is not None:
        assessed = quote_judge.assess(text, quote)
        if assessed in {"supports", "contradicts"}:
            verdict = assessed
        elif assessed != "abstain":
            errors.append(f"NG-LABEL-003: {path} quote judge returned {assessed!r}")
            return
    if verdict == "contradicts":
        errors.append(f"NG-LABEL-002: {path} cited quote does not support the claim")
    elif verdict == "inconclusive":
        errors.append(
            f"NG-LABEL-003: {path} cited quote support is inconclusive without a judge"
        )


def _check_observed_claim(
    claim: dict[str, Any],
    path: str,
    errors: list[str],
    quote_judge: Any = None,
) -> None:
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
    _check_quote(claim, path, errors, quote_judge)


def _check_kill(
    data: dict[str, Any],
    is_v12: bool,
    is_v13: bool,
    errors: list[str],
    quote_judge: Any = None,
) -> None:
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
        if isinstance(item.get("quote"), str):
            _check_quote(item, path, errors, quote_judge)
        if is_v13:
            ignored = ignored_cost_inputs(item, data, index)
            if ignored:
                detail = ", ".join(ignored)
                derivation = item.get("derivation") if isinstance(item.get("derivation"), dict) else {}
                excuse = ""
                if derivation.get("formula") == "identity":
                    excuse = " and has no written justification"
                errors.append(
                    f"NG-KILL-006: {path} derivation ignores cost inputs present "
                    f"in the packet ({detail}){excuse}"
                )
        if not is_v13:
            continue
        recomputed, problems = recompute_kill_threshold(item)
        if problems or recomputed is None:
            detail = "; ".join(problems) if problems else "not recomputed"
            errors.append(f"NG-KILL-005: {path} {detail}")
            continue
        if isinstance(threshold, (int, float)) and not isinstance(threshold, bool):
            if not _close(float(threshold), recomputed):
                errors.append(
                    f"NG-KILL-004: {path} threshold {threshold} != recomputed {recomputed:g}"
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


def _check_research(
    data: dict[str, Any],
    is_v12: bool,
    errors: list[str],
    quote_judge: Any = None,
) -> None:
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
                claim,
                f"appendix.research_claims[{claim.get('claim_id')}]",
                errors,
                quote_judge,
            )
    for index, claim in enumerate(research.get("observed_claims") or []):
        if not isinstance(claim, dict):
            errors.append(f"NG-RESEARCH-001: observed_claims[{index}] must be an object")
            continue
        _check_observed_claim(
            claim, f"research.observed_claims[{index}]", errors, quote_judge
        )
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


def _check_claim_list(
    data: dict[str, Any], errors: list[str], quote_judge: Any
) -> None:
    claims = data.get("claims")
    if not isinstance(claims, list):
        return
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            continue
        if _claim_label(claim) != "OBSERVED":
            continue
        path = f"claims[{index}]"
        if isinstance(claim.get("quote"), str):
            _check_quote(claim, path, errors, quote_judge)


def _check_observed_fields(node: Any, path: str, errors: list[str]) -> None:
    """Placeholder dates and words on every string of an OBSERVED object."""
    if isinstance(node, dict):
        if _claim_label(node) == "OBSERVED":
            for key, value in node.items():
                if key in {"claim_label", "label"}:
                    continue
                pairs: list[tuple[str, str]] = []
                if isinstance(value, str):
                    pairs.append((key, value))
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        if isinstance(item, str):
                            pairs.append((f"{key}[{index}]", item))
                for field, text in pairs:
                    if date_is_placeholder(text):
                        where = f"{path}.{field}" if path else field
                        errors.append(
                            f"NG-LABEL-001: {where} OBSERVED date is a placeholder"
                        )
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            _check_observed_fields(value, child, errors)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _check_observed_fields(value, f"{path}[{index}]", errors)


def packaging_errors(
    data: dict[str, Any],
    packet_type: str,
    quote_judge: Any = None,
) -> list[str]:
    """Bake-off checks for opportunity and commercial packets."""
    key = (packet_type or "").strip().lower().replace(" ", "_").replace("-", "_")
    if key not in {"opportunity", "commercial"}:
        return []
    if not isinstance(data, dict):
        return []
    version = data.get("schema_version")
    is_v12 = _version_ge(version, BAKEOFF_VERSION)
    is_v13 = _version_ge(version, SCHEMA_VERSION)
    errors: list[str] = []
    _check_observed_fields(data, "", errors)
    _check_kill(data, is_v12, is_v13, errors, quote_judge)
    _check_handoff(data, is_v12, errors)
    _check_contradictions(data, is_v12, errors)
    _check_research(data, is_v12, errors, quote_judge)
    _check_page(data, is_v12, errors)
    _check_claim_list(data, errors, quote_judge)
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
    """Return a schema 1.3.0 packet. Does not invent buyers, revenue, or prices."""
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
    """Synthetic seat-floor opportunity used as the 1.3.0 sample. Fixture data only."""
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
                "derivation": identity_derivation(0),
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
