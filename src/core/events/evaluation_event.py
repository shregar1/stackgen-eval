"""Base evaluation event."""

import time


class EvaluationEvent:
    """Base class for all evaluation lifecycle events."""
    def __init__(self):
        self.timestamp = time.time()
