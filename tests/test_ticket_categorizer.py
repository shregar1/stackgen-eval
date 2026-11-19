"""Unit tests for TicketDescriptionCategorizer adhering to strict single-class OOP design."""

from src.evaluators.ticket_description_categorizer import TicketDescriptionCategorizer
from src.models.ticket_category import TicketCategory


class TestTicketDescriptionCategorizer:
    """Class-based test suite for ticket description categorization."""

    def test_categorize_critical_defect(self):
        categorizer = TicketDescriptionCategorizer()
        category = categorizer.categorize("Blocker: payments timeout on checkout")
        assert category == TicketCategory.CRITICAL_DEFECT

    def test_categorize_cosmetic_change(self):
        categorizer = TicketDescriptionCategorizer()
        category = categorizer.categorize("Update status page copy for maintenance window - blocks release notes")
        assert category == TicketCategory.COSMETIC_CHANGE

    def test_categorize_cosmetic_typo(self):
        categorizer = TicketDescriptionCategorizer()
        category = categorizer.categorize("Fix typo in README documentation")
        assert category == TicketCategory.COSMETIC_CHANGE

    def test_categorize_task_or_feature(self):
        categorizer = TicketDescriptionCategorizer()
        category = categorizer.categorize("Implement user profile avatar upload")
        assert category == TicketCategory.TASK_OR_FEATURE

    def test_explain_categorization(self):
        categorizer = TicketDescriptionCategorizer()
        explanation = categorizer.explain_categorization(
            "Blocker: payments timeout on checkout",
            "p99 latency exceeded threshold"
        )
        assert explanation["category"] == "critical_defect"
        assert explanation["is_critical"] is True
        assert explanation["is_cosmetic"] is False
        assert "Production-impacting" in explanation["operational_impact"]

    def test_explain_cosmetic_categorization(self):
        categorizer = TicketDescriptionCategorizer()
        explanation = categorizer.explain_categorization(
            "Update status page copy for maintenance window"
        )
        assert explanation["category"] == "cosmetic_change"
        assert explanation["is_critical"] is False
        assert explanation["is_cosmetic"] is True
