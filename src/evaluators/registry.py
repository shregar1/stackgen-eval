"""Registry & Factory Pattern: Dynamic discovery and construction of rules and evaluators."""

from typing import Callable, Dict, List, Type
from src.config import EvaluationConfig, default_config
from src.evaluators.base import BaseRule, BaseEvaluator
from src.evaluators.chain import EvaluationHandler, DeterministicRuleHandler, LLMJudgeHandler
from src.evaluators.strategies import IEvaluationStrategy, TieredHybridStrategy, DeterministicOnlyStrategy


class RuleRegistry:
    """Central registry for deterministic rules allowing plugin-style discovery."""

    _registry: Dict[str, Type[BaseRule]] = {}

    @classmethod
    def register(cls, rule_id: str) -> Callable[[Type[BaseRule]], Type[BaseRule]]:
        def decorator(subclass: Type[BaseRule]) -> Type[BaseRule]:
            cls._registry[rule_id] = subclass
            return subclass
        return decorator

    @classmethod
    def get_all_rules(cls, config: EvaluationConfig = default_config) -> List[BaseRule]:
        return [rule_cls(config) for rule_cls in cls._registry.values()]


class EvaluatorFactory:
    """Factory Method pattern constructing configured evaluation pipelines."""

    @staticmethod
    def create_chain(
        deterministic_engine: BaseEvaluator,
        llm_judge_engine: BaseEvaluator
    ) -> EvaluationHandler:
        """Construct the Chain of Responsibility."""
        det_handler = DeterministicRuleHandler(deterministic_engine)
        judge_handler = LLMJudgeHandler(llm_judge_engine)
        det_handler.set_next(judge_handler)
        return det_handler

    @staticmethod
    def create_strategy(mode: str) -> IEvaluationStrategy:
        """Instantiate evaluation strategy based on configuration mode."""
        if mode == "deterministic_only":
            return DeterministicOnlyStrategy()
        return TieredHybridStrategy()
