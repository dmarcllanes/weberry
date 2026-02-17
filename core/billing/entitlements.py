from core.models.user import User, PlanType
from core.models.project import Project
from core.billing.plans import get_plan_limits


def can_create_project(user: User, project_count: int) -> bool:
    limits = get_plan_limits(user.plan)
    return project_count < limits["max_projects"]


def can_regenerate(user: User, project: Project) -> bool:
    if user.plan == PlanType.DRAFTER:
        return False
    limits = get_plan_limits(user.plan)
    return project.ai_usage.generation_calls < limits["generation_calls"]


def can_replan(user: User, project: Project) -> bool:
    if user.plan == PlanType.DRAFTER:
        return False
    limits = get_plan_limits(user.plan)
    return project.ai_usage.planner_calls < limits["planner_calls"]


def can_change_theme(user: User) -> bool:
    return user.plan != PlanType.DRAFTER


def can_use_custom_domain(user: User) -> bool:
    return user.plan != PlanType.DRAFTER


def can_export_files(user: User) -> bool:
    return user.plan != PlanType.DRAFTER
