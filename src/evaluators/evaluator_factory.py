"""EvaluatorFactory method pattern."""

from src.evaluators.base_evaluator import BaseEvaluator
from src.evaluators.evaluation_handler import EvaluationHandler
from src.evaluators.deterministic_rule_handler import DeterministicRuleHandler
from src.evaluators.llm_judge_handler import LLMJudgeHandler
from src.evaluators.i_evaluation_strategy import IEvaluationStrategy
from src.evaluators.tiered_hybrid_strategy import TieredHybridStrategy
from src.evaluators.deterministic_only_strategy import DeterministicOnlyStrategy


class EvaluatorFactory:
    """Factory Method pattern constructing configured evaluation pipelines."""

    @staticmethod
    def create_chain(
        deterministic_engine: BaseEvaluator,
        llm_judge_engine: BaseEvaluator,
        enable_cache: bool = True
    ) -> EvaluationHandler:
        """Construct the Chain of Responsibility, decorated with caching."""
        det_handler = DeterministicRuleHandler(deterministic_engine)
        
        target_judge = llm_judge_engine
        if enable_cache:
            from src.decorators.cached_evaluator_decorator import CachedEvaluatorDecorator
            target_judge = CachedEvaluatorDecorator(llm_judge_engine)

        judge_handler = LLMJudgeHandler(target_judge)
        det_handler.set_next(judge_handler)
        return det_handler

    @staticmethod
    def create_strategy(mode: str) -> IEvaluationStrategy:
        """Instantiate evaluation strategy based on configuration mode."""
        if mode == "deterministic_only":
            return DeterministicOnlyStrategy()
        return TieredHybridStrategy()
