"""Ticket description categorizer distinguishing cosmetic changes from critical defects."""

import re
from typing import Dict, Any, List
from src.models.ticket_category import TicketCategory


class TicketDescriptionCategorizer:
    """
    Categorizes tickets based on title and description into:
    1. CRITICAL_DEFECT: 'Actual reason problematic stuff' (crashes, payment timeouts, data corruption).
    2. COSMETIC_CHANGE: 'Cosmetic changes' (status page copy, release notes wording, typos, docs).
    3. TASK_OR_FEATURE: Routine developmental chores or standard features.
    """

    CRITICAL_KEYWORDS: List[str] = [
        "timeout", "timed out", "payment", "checkout", "crash", "exception",
        "500", "502", "503", "504", "outage", "data loss", "corruption",
        "deadlock", "memory leak", "oom", "latency spike", "security vulnerability",
        "critical", "fatal", "broken", "unresponsive", "segfault"
    ]

    COSMETIC_KEYWORDS: List[str] = [
        "copy update", "status page copy", "release notes", "wording",
        "typo", "readme", "documentation", "docstring", "banner text",
        "spelling", "formatting", "font", "css tweak", "color palette",
        "cosmetic", "clarification", "ui text"
    ]

    def categorize(self, title: str, description: str = "") -> TicketCategory:
        """Categorize a ticket based on title and description."""
        combined_text = f"{title} {description}".lower()

        # Check for cosmetic indicators first if title explicitly denotes copy/docs
        is_cosmetic_match = any(
            re.search(r"\b" + re.escape(kw) + r"\b", combined_text)
            for kw in self.COSMETIC_KEYWORDS
        )
        is_critical_match = any(
            re.search(r"\b" + re.escape(kw) + r"\b", combined_text)
            for kw in self.CRITICAL_KEYWORDS
        )

        # If it specifically mentions status page copy or release notes wording without functional breakdown
        if is_cosmetic_match and not is_critical_match:
            return TicketCategory.COSMETIC_CHANGE

        if is_critical_match:
            return TicketCategory.CRITICAL_DEFECT

        if is_cosmetic_match:
            return TicketCategory.COSMETIC_CHANGE

        return TicketCategory.TASK_OR_FEATURE

    def explain_categorization(self, title: str, description: str = "") -> Dict[str, Any]:
        """Provide detailed metadata and justification for the ticket categorization."""
        category = self.categorize(title, description)
        if category == TicketCategory.CRITICAL_DEFECT:
            impact = "Production-impacting defect that threatens system availability or core workflows."
        elif category == TicketCategory.COSMETIC_CHANGE:
            impact = "Non-functional, superficial change that does not impact system execution or data integrity."
        else:
            impact = "Routine engineering feature or chore."

        return {
            "title": title,
            "category": category.value,
            "is_critical": category == TicketCategory.CRITICAL_DEFECT,
            "is_cosmetic": category == TicketCategory.COSMETIC_CHANGE,
            "operational_impact": impact
        }
