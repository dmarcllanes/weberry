from datetime import datetime, timezone

from core.models.user import User
from core.models.project import Project
from core.ai.schemas import SitePlan
from core.ai.planner import run_planner
from core.ai.html_generator import run_html_generator
from core.ai.css_generator import run_css_generator
from core.models.site_version import SiteVersion
from core.state_machine.states import ProjectState
from core.state_machine.engine import transition, transition_to_error
from core.limits.ai_limits import check_ai_limit, increment_usage
from core.limits.rate_limits import check_rate_limit, record_call
from core.limits.cooldowns import check_cooldown
from core.errors import AIGenerationError


def generate_plan(project: Project, user: User) -> SitePlan:
    """
    Generate a site plan for a project.

    Enforces: state -> limits -> cooldown -> rate limit -> AI call -> validate -> increment -> transition.
    The ONLY entry point for planner AI calls.
    """
    # 1. State check: must be in MEMORY_READY
    # (transition() will enforce this via is_valid_transition)

    # 2. Limit check
    check_ai_limit(project.ai_usage, user.plan, "planner")

    # 3. Cooldown check
    check_cooldown(project.ai_usage)

    # 4. Rate limit check
    check_rate_limit(user.id)

    # 5. Call planner
    try:
        plan = run_planner(project.brand_memory)
    except Exception as e:
        transition_to_error(project)
        raise AIGenerationError("planner", str(e)) from e

    # 6. Persist plan on project
    project.site_plan = plan

    # 7. Increment usage + record call
    increment_usage(project.ai_usage, "planner")
    project.ai_usage.last_ai_call_at = datetime.now(timezone.utc)
    record_call(user.id)

    # 8. Transition state: MEMORY_READY -> PLAN_READY
    transition(project, ProjectState.PLAN_READY)

    return plan


def generate_site(project: Project, user: User) -> SiteVersion:
    """
    Generate HTML + CSS for a project.

    Two internal LLM calls (HTML then CSS), but ONE usage increment for the user.
    The ONLY entry point for site generation AI calls.
    """
    # 1. Limit check
    check_ai_limit(project.ai_usage, user.plan, "generation")

    # 2. Cooldown check
    check_cooldown(project.ai_usage)

    # 3. Rate limit check
    check_rate_limit(user.id)

    # 4. Generate HTML
    try:
        html_output = run_html_generator(project.site_plan, project.brand_memory)
    except Exception as e:
        transition_to_error(project)
        raise AIGenerationError("html_generator", str(e)) from e

    # 5. Generate CSS
    try:
        css_output = run_css_generator(html_output.html, project.brand_memory)
    except Exception as e:
        transition_to_error(project)
        raise AIGenerationError("css_generator", str(e)) from e

    # 6. Create site version
    current_version = project.site_version.version if project.site_version else 0
    site_version = SiteVersion(
        html=html_output.html,
        css=css_output.css,
        version=current_version + 1,
    )
    project.site_version = site_version

    # 7. Increment usage + record call
    increment_usage(project.ai_usage, "generation")
    project.ai_usage.last_ai_call_at = datetime.now(timezone.utc)
    record_call(user.id)

    # 8. Transition state: PLAN_APPROVED -> SITE_GENERATED
    transition(project, ProjectState.SITE_GENERATED)

    return site_version
