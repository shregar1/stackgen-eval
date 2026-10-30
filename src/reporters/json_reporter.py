"""JSON format reporter."""

import json
from src.models.evaluation_batch_result import EvaluationBatchResult


class JSONReporter:
    """Renders evaluation results matching the take-home specification format."""

    @staticmethod
    def render(batch: EvaluationBatchResult, indent: int = 2) -> str:
        return json.dumps(batch.to_spec_dict(), indent=indent)
