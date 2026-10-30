"""Rule registry for dynamic discovery of evaluation rules."""

from typing import Dict, List, Type
from src.config import EvaluationConfig, default_config
from src.evaluators.base_rule import BaseRule
from src.evaluators.rule_registration_decorator import RuleRegistrationDecorator


class RuleRegistry:
    """Central registry for deterministic rules allowing plugin-style discovery."""

    _registry: Dict[str, Type[BaseRule]] = {}

    @classmethod
    def register(cls, rule_id: str) -> RuleRegistrationDecorator:
        return RuleRegistrationDecorator(cls._registry, rule_id)

    @classmethod
    def get_all_rules(cls, config: EvaluationConfig = default_config) -> List[BaseRule]:
        return [rule_cls(config) for rule_cls in cls._registry.values()]
