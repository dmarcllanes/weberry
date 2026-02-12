from core.models.user import PlanType

PLAN_LIMITS = {
    PlanType.FREE: {
        "max_projects": 1,
        "planner_calls": 1,
        "generation_calls": 1,
    },
    PlanType.PAID: {
        "max_projects": 10,
        "planner_calls": 5,
        "generation_calls": 5,
    },
}


def get_plan_limits(plan: PlanType) -> dict:
    return PLAN_LIMITS[plan]
