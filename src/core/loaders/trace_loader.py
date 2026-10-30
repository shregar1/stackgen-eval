"""Trace loader component."""

import os
import json
from typing import List
from src.models.trace import Trace


class TraceLoader:
    """Encapsulates loading and validation of machine-readable trace datasets."""

    @classmethod
    def load(cls, path: str) -> List[Trace]:
        """Load and validate traces from JSON file."""
        if not os.path.isabs(path):
            # trace_loader.py is in src/core/loaders/ -> project root is 4 dirname calls
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            resolved_path = os.path.join(project_root, path)
            if os.path.exists(resolved_path):
                path = resolved_path

        if not os.path.exists(path):
            raise FileNotFoundError(f"Traces file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("Traces JSON file must contain a top-level array of trace objects.")

        return [Trace.model_validate(t) for t in raw_data]
