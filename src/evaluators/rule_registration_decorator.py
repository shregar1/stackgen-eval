"""Rule registration decorator class."""

from typing import Dict, Type
from src.evaluators.base_rule import BaseRule


class RuleRegistrationDecorator:
    """Callable class-based decorator for registering rules."""

    def __init__(self, registry: Dict[str, Type[BaseRule]], rule_id: str):
        self.registry = registry
        self.rule_id = rule_id

    def __call__(self, subclass: Type[BaseRule]) -> Type[BaseRule]:
        self.registry[self.rule_id] = subclass
        return subclass
