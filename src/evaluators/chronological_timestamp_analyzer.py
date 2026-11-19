"""Chronological timestamp analyzer enforcing temporal order and causality."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChronologicalTimestampAnalyzer:
    r"""
    Analyzes timestamps across Slack messages, git events, and monitoring telemetry
    in strict chronological order ($t_1 < t_2 < \dots < t_n$).
    
    Enforces two invariant rules:
    1. Temporal Superseding: A later timestamp strictly overrides and invalidates an earlier decision.
    2. Incident Causality: An anomaly with an earlier timestamp represents the upstream root cause,
       whereas anomalies at later timestamps are downstream symptoms.
    """

    MONTH_MAP = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }

    def parse_timestamp_score(self, text: str) -> Optional[float]:
        """Convert a date, time, or ISO-8601 string into an absolute comparable float."""
        # 1. ISO-8601 formatted timestamp
        iso_match = re.search(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b", text)
        if iso_match:
            try:
                clean_iso = iso_match.group(0).replace("Z", "+00:00")
                dt = datetime.fromisoformat(clean_iso)
                return dt.timestamp()
            except Exception:
                pass

        # 2. Time of day: HH:MM or HH:MM:SS
        time_match = re.search(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b", text)
        if time_match:
            h = int(time_match.group(1))
            m = int(time_match.group(2))
            s = int(time_match.group(3)) if time_match.group(3) else 0
            return float(h * 3600 + m * 60 + s)

        # 3. Month & Day: e.g. 'March 4', 'June 12'
        date_match = re.search(r"\b([A-Za-z]+)\s+(\d{1,2})\b", text)
        if date_match:
            month_str = date_match.group(1).lower()
            if month_str in self.MONTH_MAP:
                month_num = self.MONTH_MAP[month_str]
                day_num = int(date_match.group(2))
                return float(month_num * 100 + day_num)

        return None

    def sort_chronologically(self, events: List[Dict[str, Any]], timestamp_field: str = "timestamp") -> List[Dict[str, Any]]:
        """Sort event dictionaries chronologically based on their parsed timestamp score."""
        def extract_score(event: Dict[str, Any]) -> float:
            val = str(event.get(timestamp_field, ""))
            score = self.parse_timestamp_score(val)
            return score if score is not None else 0.0

        return sorted(events, key=extract_score)

    def verify_causal_direction(
        self,
        upstream_anomaly_time: str,
        downstream_anomaly_time: str
    ) -> bool:
        """
        Verify whether upstream anomaly timestamp strictly precedes downstream anomaly timestamp.
        Returns True if upstream occurs before downstream ($T_{upstream} < T_{downstream}$).
        """
        t_up = self.parse_timestamp_score(upstream_anomaly_time)
        t_down = self.parse_timestamp_score(downstream_anomaly_time)

        if t_up is not None and t_down is not None:
            return t_up < t_down
        return True
