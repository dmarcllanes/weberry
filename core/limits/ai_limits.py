from core.models.ai_usage import AIUsage
from core.errors import AILimitExceeded

# Maximum AI calls per project (applies to both planner and generation actions).
# This is an abuse-prevention limit, not a monetization limit.
AI_CALLS_PER_PROJECT = 10


def check_ai_limit(usage: AIUsage, action: str) -> None:
    """Raise AILimitExceeded if the project has hit its per-project call quota."""
    if action == "planner":
        if usage.planner_calls >= AI_CALLS_PER_PROJECT:
            raise AILimitExceeded(action, "project")
    elif action == "generation":
        if usage.generation_calls >= AI_CALLS_PER_PROJECT:
            raise AILimitExceeded(action, "project")


def increment_usage(usage: AIUsage, action: str) -> None:
    """Increment the usage counter for the given action."""
    if action == "planner":
        usage.planner_calls += 1
    elif action == "generation":
        usage.generation_calls += 1
