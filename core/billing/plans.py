from core.models.user import PlanType

PLAN_LIMITS = {
    PlanType.DRAFTER: {
        "max_projects": 1,
        "planner_calls": 1,
        "generation_calls": 1,
    },
    PlanType.VALIDATOR: {
        "max_projects": 3,
        "planner_calls": 10,
        "generation_calls": 10,
    },
    PlanType.AGENCY: {
        "max_projects": float("inf"),
        "planner_calls": float("inf"),
        "generation_calls": float("inf"),
    },
}


def get_plan_limits(plan: PlanType) -> dict:
    return PLAN_LIMITS[plan]
