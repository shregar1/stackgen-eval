"""TraceCaretaker implementation for managing trace snapshot history and checkpoints."""

from typing import Dict, List, Optional
from src.memento.trace_memento import TraceMemento


class TraceCaretaker:
    """
    Caretaker responsible for keeping and retrieving trace mementos across
    counterfactual simulation branches without exposing internal memento state.
    """

    def __init__(self):
        self._checkpoints: Dict[str, TraceMemento] = {}
        self._history_stack: List[TraceMemento] = []

    def save_checkpoint(self, tag: str, memento: TraceMemento) -> None:
        """Store a labeled memento checkpoint."""
        self._checkpoints[tag] = memento
        self._history_stack.append(memento)

    def get_checkpoint(self, tag: str) -> Optional[TraceMemento]:
        """Retrieve a labeled memento checkpoint."""
        return self._checkpoints.get(tag)

    def pop_last_checkpoint(self) -> Optional[TraceMemento]:
        """Pop the most recent memento from history for undo operations."""
        if not self._history_stack:
            return None
        return self._history_stack.pop()

    def list_checkpoints(self) -> List[str]:
        """Return all stored checkpoint tags."""
        return list(self._checkpoints.keys())

    def clear(self) -> None:
        """Clear all stored checkpoints and history."""
        self._checkpoints.clear()
        self._history_stack.clear()
