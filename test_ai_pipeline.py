"""
AI Pipeline Test Suite
======================
Run:  uv run python test_ai_pipeline.py
      uv run python test_ai_pipeline.py --live   (calls Claude API, costs ~$0.03)

Tests are grouped by file. Each test prints PASS or FAIL.
Modify as you add/change files.
"""

import sys
from datetime import datetime, timezone, timedelta

LIVE_MODE = "--live" in sys.argv
passed = 0
failed = 0


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}")
        print(f"        {type(e).__name__}: {e}")
        failed += 1


# ============================================================
# config/settings.py
# ============================================================
print("\n--- config/settings.py ---")

def test_settings_loads():
    from config.settings import (
        NVIDIA_API_KEY, NVIDIA_MODEL, AI_LIMITS,
        RATE_LIMIT_MAX_CALLS, RATE_LIMIT_WINDOW_SECONDS,
        AI_COOLDOWN_SECONDS,
    )
    assert isinstance(AI_LIMITS, dict)
    assert "FREE" in AI_LIMITS and "PAID" in AI_LIMITS
    assert AI_LIMITS["FREE"]["planner_calls"] == 1
    assert AI_LIMITS["PAID"]["planner_calls"] == 5
    assert isinstance(RATE_LIMIT_MAX_CALLS, int)
    assert isinstance(AI_COOLDOWN_SECONDS, int)

test("settings load and have correct values", test_settings_loads)


# ============================================================
# core/errors.py
# ============================================================
print("\n--- core/errors.py ---")

def test_error_hierarchy():
    from core.errors import (
        CoreError, InvalidStateTransition, AILimitExceeded,
        AIRateLimited, AICooldownActive, AIGenerationError,
        AIValidationError, GuardFailure,
    )
    from core.state_machine.states import ProjectState
    # All inherit from CoreError
    assert issubclass(InvalidStateTransition, CoreError)
    assert issubclass(AILimitExceeded, CoreError)
    assert issubclass(AIRateLimited, CoreError)
    assert issubclass(AICooldownActive, CoreError)
    assert issubclass(AIGenerationError, CoreError)
    assert issubclass(AIValidationError, CoreError)
    assert issubclass(GuardFailure, CoreError)

def test_error_messages():
    from core.errors import InvalidStateTransition, AILimitExceeded, AICooldownActive
    from core.state_machine.states import ProjectState
    e1 = InvalidStateTransition(ProjectState.DRAFT, ProjectState.PUBLISHED)
    assert "draft" in str(e1) and "published" in str(e1)
    e2 = AILimitExceeded("planner", "FREE")
    assert "planner" in str(e2) and "FREE" in str(e2)
    e3 = AICooldownActive(15.0)
    assert "15" in str(e3)

test("all errors inherit from CoreError", test_error_hierarchy)
test("error messages contain context", test_error_messages)


# ============================================================
# core/state_machine/states.py
# ============================================================
print("\n--- core/state_machine/states.py ---")

def test_all_states_exist():
    from core.state_machine.states import ProjectState
    expected = [
        "DRAFT", "INPUT_READY", "MEMORY_READY", "PLAN_READY",
        "PLAN_APPROVED", "SITE_GENERATED", "PREVIEW", "PUBLISHED", "ERROR",
    ]
    for name in expected:
        assert hasattr(ProjectState, name), f"Missing state: {name}"

test("all 9 states exist", test_all_states_exist)


# ============================================================
# core/models/user.py
# ============================================================
print("\n--- core/models/user.py ---")

def test_user_creation():
    from core.models.user import User, PlanType
    u = User(id="u1", email="a@b.com")
    assert u.plan == PlanType.FREE  # default is FREE
    u2 = User(id="u2", email="b@b.com", plan=PlanType.PAID)
    assert u2.plan == PlanType.PAID

test("user defaults to FREE plan", test_user_creation)


# ============================================================
# core/models/brand_memory.py
# ============================================================
print("\n--- core/models/brand_memory.py ---")

def test_brand_memory():
    from core.models.brand_memory import BrandMemory
    bm = BrandMemory(
        business_name="Test", website_type="portfolio", primary_goal="showcase"
    )
    assert bm.theme == "professional"  # default
    assert bm.services == []  # default empty list
    assert bm.primary_color == "#2563eb"

test("brand memory has sensible defaults", test_brand_memory)


# ============================================================
# core/models/ai_usage.py
# ============================================================
print("\n--- core/models/ai_usage.py ---")

def test_ai_usage_defaults():
    from core.models.ai_usage import AIUsage
    u = AIUsage()
    assert u.planner_calls == 0
    assert u.generation_calls == 0
    assert u.last_ai_call_at is None

test("ai_usage starts at zero", test_ai_usage_defaults)


# ============================================================
# core/models/site_version.py
# ============================================================
print("\n--- core/models/site_version.py ---")

def test_site_version():
    from core.models.site_version import SiteVersion
    sv = SiteVersion(html="<h1>hi</h1>", css="h1{color:red}")
    assert sv.version == 1
    assert sv.is_published is False

test("site_version defaults", test_site_version)


# ============================================================
# core/models/project.py
# ============================================================
print("\n--- core/models/project.py ---")

def test_project_defaults():
    from core.models.project import Project
    from core.state_machine.states import ProjectState
    p = Project(id="p1", user_id="u1")
    assert p.state == ProjectState.DRAFT
    assert p.brand_memory is None
    assert p.site_plan is None
    assert p.site_version is None
    assert p.ai_usage.planner_calls == 0

test("project starts in DRAFT with empty fields", test_project_defaults)


# ============================================================
# core/state_machine/transitions.py
# ============================================================
print("\n--- core/state_machine/transitions.py ---")

def test_valid_transitions():
    from core.state_machine.transitions import is_valid_transition
    from core.state_machine.states import ProjectState
    # Happy path
    assert is_valid_transition(ProjectState.DRAFT, ProjectState.INPUT_READY)
    assert is_valid_transition(ProjectState.INPUT_READY, ProjectState.MEMORY_READY)
    assert is_valid_transition(ProjectState.MEMORY_READY, ProjectState.PLAN_READY)
    assert is_valid_transition(ProjectState.PLAN_READY, ProjectState.PLAN_APPROVED)
    assert is_valid_transition(ProjectState.PLAN_APPROVED, ProjectState.SITE_GENERATED)
    assert is_valid_transition(ProjectState.SITE_GENERATED, ProjectState.PREVIEW)
    assert is_valid_transition(ProjectState.PREVIEW, ProjectState.PUBLISHED)
    assert is_valid_transition(ProjectState.ERROR, ProjectState.DRAFT)
    # Invalid
    assert not is_valid_transition(ProjectState.DRAFT, ProjectState.PUBLISHED)
    assert not is_valid_transition(ProjectState.PUBLISHED, ProjectState.DRAFT)
    assert not is_valid_transition(ProjectState.DRAFT, ProjectState.SITE_GENERATED)

def test_ai_transitions():
    from core.state_machine.transitions import get_ai_action
    from core.state_machine.states import ProjectState
    assert get_ai_action(ProjectState.MEMORY_READY) == "planner"
    assert get_ai_action(ProjectState.PLAN_APPROVED) == "generation"
    assert get_ai_action(ProjectState.DRAFT) is None

test("valid transitions follow happy path", test_valid_transitions)
test("AI actions mapped to correct states", test_ai_transitions)


# ============================================================
# core/state_machine/engine.py
# ============================================================
print("\n--- core/state_machine/engine.py ---")

def test_engine_transition():
    from core.state_machine.engine import transition, transition_to_error
    from core.state_machine.states import ProjectState
    from core.models.project import Project
    from core.errors import InvalidStateTransition
    p = Project(id="p1", user_id="u1")
    transition(p, ProjectState.INPUT_READY)
    assert p.state == ProjectState.INPUT_READY
    # Invalid should raise
    try:
        transition(p, ProjectState.PUBLISHED)
        assert False, "should have raised"
    except InvalidStateTransition:
        pass
    assert p.state == ProjectState.INPUT_READY  # unchanged

def test_engine_error_transition():
    from core.state_machine.engine import transition_to_error
    from core.state_machine.states import ProjectState
    from core.models.project import Project
    p = Project(id="p1", user_id="u1")
    transition_to_error(p)
    assert p.state == ProjectState.ERROR

test("engine enforces valid transitions", test_engine_transition)
test("error transition always works", test_engine_error_transition)


# ============================================================
# core/state_machine/guards.py
# ============================================================
print("\n--- core/state_machine/guards.py ---")

def test_guard_brand_memory():
    from core.state_machine.guards import run_guards
    from core.state_machine.states import ProjectState
    from core.models.project import Project
    from core.models.brand_memory import BrandMemory
    from core.errors import GuardFailure
    p = Project(id="p1", user_id="u1")
    # No brand memory -> guard fails
    try:
        run_guards(p, ProjectState.PLAN_READY)
        assert False
    except GuardFailure:
        pass
    # With brand memory -> guard passes
    p.brand_memory = BrandMemory(
        business_name="Test", website_type="portfolio", primary_goal="showcase"
    )
    run_guards(p, ProjectState.PLAN_READY)

def test_guard_site_plan():
    from core.state_machine.guards import run_guards
    from core.state_machine.states import ProjectState
    from core.models.project import Project
    from core.ai.schemas import SitePlan, SectionPlan
    from core.errors import GuardFailure
    p = Project(id="p1", user_id="u1")
    try:
        run_guards(p, ProjectState.SITE_GENERATED)
        assert False
    except GuardFailure:
        pass
    p.site_plan = SitePlan(
        sections=[SectionPlan(id="hero", title="Hero", purpose="x", content_notes="x")],
        page_title="Test", meta_description="test",
    )
    run_guards(p, ProjectState.SITE_GENERATED)

test("guard blocks without brand memory", test_guard_brand_memory)
test("guard blocks without site plan", test_guard_site_plan)


# ============================================================
# core/limits/ai_limits.py
# ============================================================
print("\n--- core/limits/ai_limits.py ---")

def test_free_plan_limit():
    from core.limits.ai_limits import check_ai_limit, increment_usage
    from core.models.ai_usage import AIUsage
    from core.models.user import PlanType
    from core.errors import AILimitExceeded
    u = AIUsage()
    check_ai_limit(u, PlanType.FREE, "planner")  # 0 < 1
    increment_usage(u, "planner")
    try:
        check_ai_limit(u, PlanType.FREE, "planner")  # 1 >= 1
        assert False
    except AILimitExceeded:
        pass

def test_paid_plan_limit():
    from core.limits.ai_limits import check_ai_limit, increment_usage
    from core.models.ai_usage import AIUsage
    from core.models.user import PlanType
    from core.errors import AILimitExceeded
    u = AIUsage(planner_calls=4)
    check_ai_limit(u, PlanType.PAID, "planner")  # 4 < 5
    increment_usage(u, "planner")
    try:
        check_ai_limit(u, PlanType.PAID, "planner")  # 5 >= 5
        assert False
    except AILimitExceeded:
        pass

test("free plan: 1 planner call allowed", test_free_plan_limit)
test("paid plan: 5 planner calls allowed", test_paid_plan_limit)


# ============================================================
# core/limits/rate_limits.py
# ============================================================
print("\n--- core/limits/rate_limits.py ---")

def test_rate_limit():
    from core.limits.rate_limits import check_rate_limit, record_call, reset
    from core.errors import AIRateLimited
    reset()
    for _ in range(10):
        record_call("rate-test-user")
    try:
        check_rate_limit("rate-test-user")
        assert False
    except AIRateLimited:
        pass
    reset()

test("rate limit triggers after max calls", test_rate_limit)


# ============================================================
# core/limits/cooldowns.py
# ============================================================
print("\n--- core/limits/cooldowns.py ---")

def test_cooldown_active():
    from core.limits.cooldowns import check_cooldown
    from core.models.ai_usage import AIUsage
    from core.errors import AICooldownActive
    u = AIUsage(last_ai_call_at=datetime.now(timezone.utc))
    try:
        check_cooldown(u)
        assert False
    except AICooldownActive:
        pass

def test_cooldown_expired():
    from core.limits.cooldowns import check_cooldown
    from core.models.ai_usage import AIUsage
    u = AIUsage(last_ai_call_at=datetime.now(timezone.utc) - timedelta(seconds=120))
    check_cooldown(u)  # should not raise

def test_cooldown_never_called():
    from core.limits.cooldowns import check_cooldown
    from core.models.ai_usage import AIUsage
    check_cooldown(AIUsage())  # should not raise

test("cooldown blocks recent call", test_cooldown_active)
test("cooldown allows after expiry", test_cooldown_expired)
test("cooldown allows first-ever call", test_cooldown_never_called)


# ============================================================
# core/ai/schemas.py
# ============================================================
print("\n--- core/ai/schemas.py ---")

def test_validate_site_plan_valid():
    from core.ai.schemas import SitePlan, SectionPlan, validate_site_plan
    plan = SitePlan(
        sections=[
            SectionPlan(id="hero", title="Hero", purpose="x", content_notes="x"),
            SectionPlan(id="about", title="About", purpose="x", content_notes="x"),
        ],
        page_title="Test", meta_description="test",
    )
    validate_site_plan(plan)

def test_validate_site_plan_empty():
    from core.ai.schemas import SitePlan, validate_site_plan
    from core.errors import AIValidationError
    try:
        validate_site_plan(SitePlan(sections=[], page_title="Test", meta_description="x"))
        assert False
    except AIValidationError:
        pass

def test_validate_site_plan_dupe_ids():
    from core.ai.schemas import SitePlan, SectionPlan, validate_site_plan
    from core.errors import AIValidationError
    try:
        validate_site_plan(SitePlan(
            sections=[
                SectionPlan(id="hero", title="A", purpose="x", content_notes="x"),
                SectionPlan(id="hero", title="B", purpose="x", content_notes="x"),
            ],
            page_title="Test", meta_description="x",
        ))
        assert False
    except AIValidationError:
        pass

test("valid site plan passes", test_validate_site_plan_valid)
test("empty sections rejected", test_validate_site_plan_empty)
test("duplicate section IDs rejected", test_validate_site_plan_dupe_ids)


# ============================================================
# core/ai/html_generator.py (validation only, no API)
# ============================================================
print("\n--- core/ai/html_generator.py (validators) ---")

def test_html_valid():
    from core.ai.html_generator import _validate_html
    _validate_html("<!DOCTYPE html><html><body><nav>x</nav><footer>x</footer></body></html>")

def test_html_rejects_script():
    from core.ai.html_generator import _validate_html
    from core.errors import AIValidationError
    try:
        _validate_html("<!DOCTYPE html><html><body><script>alert(1)</script><nav>x</nav><footer>x</footer></body></html>")
        assert False
    except AIValidationError:
        pass

def test_html_rejects_missing_nav():
    from core.ai.html_generator import _validate_html
    from core.errors import AIValidationError
    try:
        _validate_html("<!DOCTYPE html><html><body><footer>x</footer></body></html>")
        assert False
    except AIValidationError:
        pass

def test_html_rejects_missing_footer():
    from core.ai.html_generator import _validate_html
    from core.errors import AIValidationError
    try:
        _validate_html("<!DOCTYPE html><html><body><nav>x</nav></body></html>")
        assert False
    except AIValidationError:
        pass

def test_html_rejects_event_handlers():
    from core.ai.html_generator import _validate_html
    from core.errors import AIValidationError
    try:
        _validate_html('<!DOCTYPE html><html><body><nav>x</nav><div onclick="bad()">x</div><footer>x</footer></body></html>')
        assert False
    except AIValidationError:
        pass

test("valid HTML passes", test_html_valid)
test("HTML rejects script tags", test_html_rejects_script)
test("HTML rejects missing nav", test_html_rejects_missing_nav)
test("HTML rejects missing footer", test_html_rejects_missing_footer)
test("HTML rejects event handlers", test_html_rejects_event_handlers)


# ============================================================
# core/ai/css_generator.py (validation only, no API)
# ============================================================
print("\n--- core/ai/css_generator.py (validators) ---")

def test_css_valid():
    from core.ai.css_generator import _validate_css
    _validate_css("body { margin: 0; } nav { background: #333; }")

def test_css_rejects_import():
    from core.ai.css_generator import _validate_css
    from core.errors import AIValidationError
    try:
        _validate_css('@import url("https://fonts.googleapis.com"); body {}')
        assert False
    except AIValidationError:
        pass

def test_css_rejects_external_url():
    from core.ai.css_generator import _validate_css
    from core.errors import AIValidationError
    try:
        _validate_css('body { background: url("https://example.com/img.png"); }')
        assert False
    except AIValidationError:
        pass

def test_css_allows_data_uri():
    from core.ai.css_generator import _validate_css
    _validate_css('body { background: url("data:image/png;base64,abc"); }')

test("valid CSS passes", test_css_valid)
test("CSS rejects @import", test_css_rejects_import)
test("CSS rejects external URLs", test_css_rejects_external_url)
test("CSS allows data URIs", test_css_allows_data_uri)


# ============================================================
# core/ai/gateway.py (full integration — LIVE only)
# ============================================================
if LIVE_MODE:
    print("\n--- core/ai/gateway.py (LIVE API calls) ---")

    from dotenv import load_dotenv
    load_dotenv()

    def test_gateway_full_pipeline():
        from core.models.user import User, PlanType
        from core.models.project import Project
        from core.models.brand_memory import BrandMemory
        from core.state_machine.states import ProjectState
        from core.state_machine.engine import transition
        from core.ai.gateway import generate_plan, generate_site
        from core.limits.rate_limits import reset

        reset()

        user = User(id="test-user", email="t@t.com", plan=PlanType.FREE)
        project = Project(id="test-project", user_id=user.id)
        project.brand_memory = BrandMemory(
            business_name="Sunrise Bakery",
            website_type="local business",
            primary_goal="Get more walk-in customers",
            description="Family-owned bakery in Portland specializing in sourdough",
            tagline="Fresh baked daily since 1995",
            services=["Sourdough Bread", "Pastries", "Custom Cakes"],
            contact_email="hello@sunrisebakery.com",
            contact_phone="(503) 555-0123",
            address="742 NE Alberta St, Portland, OR",
        )

        transition(project, ProjectState.INPUT_READY)
        transition(project, ProjectState.MEMORY_READY)

        # Planner
        plan = generate_plan(project, user)
        assert project.state == ProjectState.PLAN_READY
        assert len(plan.sections) >= 3
        assert plan.page_title
        print(f"        Plan: {plan.page_title} ({len(plan.sections)} sections)")

        # Approve + generate
        transition(project, ProjectState.PLAN_APPROVED)
        site = generate_site(project, user)
        assert project.state == ProjectState.SITE_GENERATED
        assert "<nav" in site.html.lower()
        assert "<footer" in site.html.lower()
        assert len(site.css) > 100
        print(f"        HTML: {len(site.html)} chars | CSS: {len(site.css)} chars")

        # Save for browser preview
        with open("test_output.html", "w") as f:
            f.write(f"<style>{site.css}</style>\n{site.html}")
        print("        Saved test_output.html")

    def test_gateway_limit_enforcement():
        from core.models.user import User, PlanType
        from core.models.project import Project
        from core.models.brand_memory import BrandMemory
        from core.models.ai_usage import AIUsage
        from core.state_machine.states import ProjectState
        from core.ai.gateway import generate_plan
        from core.errors import AILimitExceeded

        user = User(id="limit-user", email="t@t.com", plan=PlanType.FREE)
        project = Project(id="limit-project", user_id=user.id, state=ProjectState.MEMORY_READY)
        project.brand_memory = BrandMemory(
            business_name="Test", website_type="test", primary_goal="test",
        )
        project.ai_usage = AIUsage(planner_calls=1)  # already used
        try:
            generate_plan(project, user)
            assert False, "should have raised"
        except AILimitExceeded:
            pass

    test("full pipeline: plan + generate (API call)", test_gateway_full_pipeline)
    test("limit enforcement blocks second call", test_gateway_limit_enforcement)
else:
    print("\n--- core/ai/gateway.py (skipped — run with --live) ---")


# ============================================================
# user_app/services/ai_service.py
# ============================================================
print("\n--- user_app/services/ai_service.py ---")

def test_service_imports():
    from user_app.services.ai_service import run_planner_for_project, run_generator_for_project
    assert callable(run_planner_for_project)
    assert callable(run_generator_for_project)

test("service functions importable", test_service_imports)


# ============================================================
# Summary
# ============================================================
total = passed + failed
print(f"\n{'='*50}")
print(f"  {passed}/{total} passed, {failed} failed")
if not LIVE_MODE:
    print("  (run with --live to test API calls)")
print(f"{'='*50}")
sys.exit(1 if failed else 0)
