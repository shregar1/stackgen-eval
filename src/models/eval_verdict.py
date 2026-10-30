"""Evaluation verdict enumeration."""

from enum import Enum


class EvalVerdict(str, Enum):
    """Pass / Fail verdict."""
    PASS = "pass"
    FAIL = "fail"
