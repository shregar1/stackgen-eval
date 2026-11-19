"""Unit tests for ChronologicalTimestampAnalyzer adhering to strict single-class OOP design."""

from src.evaluators.chronological_timestamp_analyzer import ChronologicalTimestampAnalyzer


class TestChronologicalTimestampAnalyzer:
    """Class-based test suite for chronological timestamp analysis."""

    def test_parse_iso_timestamp(self):
        analyzer = ChronologicalTimestampAnalyzer()
        score = analyzer.parse_timestamp_score("2024-03-04T10:00:00Z")
        assert score is not None
        assert score > 0

    def test_parse_time_of_day(self):
        analyzer = ChronologicalTimestampAnalyzer()
        score_1004 = analyzer.parse_timestamp_score("10:04")
        score_1005 = analyzer.parse_timestamp_score("10:05")
        assert score_1004 is not None
        assert score_1005 is not None
        assert score_1004 < score_1005

    def test_parse_month_and_day(self):
        analyzer = ChronologicalTimestampAnalyzer()
        march_4 = analyzer.parse_timestamp_score("March 4")
        june_12 = analyzer.parse_timestamp_score("June 12")
        assert march_4 is not None
        assert june_12 is not None
        assert march_4 < june_12

    def test_verify_causal_direction(self):
        analyzer = ChronologicalTimestampAnalyzer()
        assert analyzer.verify_causal_direction("10:04", "10:05") is True
        assert analyzer.verify_causal_direction("10:05", "10:04") is False

    def test_sort_chronologically(self):
        analyzer = ChronologicalTimestampAnalyzer()
        events = [
            {"name": "checkout_spike", "timestamp": "10:05"},
            {"name": "payments_spike", "timestamp": "10:04"},
            {"name": "alert_fired", "timestamp": "10:06"}
        ]
        sorted_events = analyzer.sort_chronologically(events)
        assert sorted_events[0]["name"] == "payments_spike"
        assert sorted_events[1]["name"] == "checkout_spike"
        assert sorted_events[2]["name"] == "alert_fired"
