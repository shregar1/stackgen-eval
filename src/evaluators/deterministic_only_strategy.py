"""Deterministic only evaluation strategy."""

from src.evaluators.i_evaluation_strategy import IEvaluationStrategy
from src.evaluators.evaluation_handler import EvaluationHandler
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict


class DeterministicOnlyStrategy(IEvaluationStrategy):
    """Cost-conscious / local-only strategy evaluating purely rule-based specifications."""

    def evaluate(self, trace: Trace, chain: EvaluationHandler) -> TraceEvaluation:
        res = chain.handle(trace)
        if res is not None and res.evaluator_type == EvaluatorType.DETERMINISTIC:
            return res
        return TraceEvaluation(
            trace_id=trace.trace_id,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
