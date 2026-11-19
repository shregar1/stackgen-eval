"""Ticket severity category enumeration."""

from enum import Enum


class TicketCategory(str, Enum):
    """Categorization of tickets based on description and operational impact."""

    CRITICAL_DEFECT = "critical_defect"  # Actual reason problematic stuff (crashes, timeouts, data loss)
    COSMETIC_CHANGE = "cosmetic_change"  # Cosmetic / copy updates (release notes, typos, status page copy)
    TASK_OR_FEATURE = "task_or_feature"  # Standard feature tasks or chores
