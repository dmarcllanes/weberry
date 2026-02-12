from core.models.ai_usage import AIUsage
from core.models.user import PlanType
from core.errors import AILimitExceeded
from config.settings import AI_LIMITS


def check_ai_limit(usage: AIUsage, plan: PlanType, action: str) -> None:
    """Raise AILimitExceeded if the user has hit their quota for this action."""
    limits = AI_LIMITS[plan.value]

    if action == "planner":
        if usage.planner_calls >= limits["planner_calls"]:
            raise AILimitExceeded(action, plan.value)
    elif action == "generation":
        if usage.generation_calls >= limits["generation_calls"]:
            raise AILimitExceeded(action, plan.value)


def increment_usage(usage: AIUsage, action: str) -> None:
    """Increment the usage counter for the given action."""
    if action == "planner":
        usage.planner_calls += 1
    elif action == "generation":
        usage.generation_calls += 1
