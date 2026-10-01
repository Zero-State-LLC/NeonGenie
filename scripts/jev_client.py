#!/usr/bin/env python3
"""Stdlib client for TypeSafe System One (Jev).

Jev answers Choice, Score, and Noul questions. It does not return prose.
The key is read from ``TYPESAFE_AI_API_KEY`` and is never logged or copied
into an error message.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable

ENV_KEY = "TYPESAFE_AI_API_KEY"
JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"


class JevError(RuntimeError):
    """Jev call failed. The message never includes the API key."""


def system_one(
    state: Any,
    questions: dict[str, Any],
    *,
    transport: Callable[..., Any] | None = None,
    model: str = JEV_MODEL,
) -> dict[str, Any]:
    """POST /v1/systemone. ``transport`` replaces urllib in tests.

    ``transport`` receives the JSON body bytes and returns response bytes
    or text. The live path reads the key from the environment only.
    """
    key = os.environ.get(ENV_KEY, "")
    if transport is None and (not isinstance(key, str) or not key.strip()):
        raise JevError("TYPESAFE_AI_API_KEY is not set")
    payload = json.dumps(
        {"model": model, "state": state, "questions": questions}
    ).encode("utf-8")
    if transport is not None:
        raw = transport(payload)
    else:
        req = urllib.request.Request(
            JEV_URL,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "neon-genie-judge/3.30",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            raise JevError(f"Jev HTTP {exc.code}") from None
        except urllib.error.URLError:
            raise JevError("Jev request failed") from None
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="replace")
    else:
        text = str(raw)
    if key and key in text:
        text = text.replace(key, "[redacted]")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        raise JevError("Jev returned non-JSON") from None
    if not isinstance(parsed, dict):
        raise JevError("Jev returned a non-object")
    return parsed
