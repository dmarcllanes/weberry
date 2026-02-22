"""
Central persistence module.
Handles all Supabase client init, JSONB serialization, and CRUD operations.
"""

import hashlib
from dataclasses import asdict
from datetime import datetime, timezone

from supabase import create_client, Client

from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY
from core.models.user import User, PlanType
from core.models.project import Project
from core.models.brand_memory import BrandMemory, LabeledAsset, ProjectIntent
from core.models.ai_usage import AIUsage
from core.models.site_version import SiteVersion
from core.ai.schemas import SitePlan, SectionPlan, CopyBlock
from core.state_machine.states import ProjectState


# --- Client ---

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _client


def get_storage():
    return get_client().storage


# --- Serialization helpers ---

def _serialize_brand_memory(bm: BrandMemory | None) -> dict | None:
    if bm is None:
        return None
    d = asdict(bm)
    # Convert Enum to value for JSON serialization
    if "project_intent" in d and hasattr(d["project_intent"], "value"):
        d["project_intent"] = d["project_intent"].value
    # Convert labeled_assets if they exist (asdict handles nested dataclasses but let's be safe)
    return d


def _deserialize_brand_memory(data: dict | None) -> BrandMemory | None:
    if data is None:
        return None
    # Convert labeled_assets dicts back to LabeledAsset instances
    if "labeled_assets" in data and data["labeled_assets"]:
        data["labeled_assets"] = [
            LabeledAsset(**a) if isinstance(a, dict) else a
            for a in data["labeled_assets"]
        ]
    # Convert project_intent string back to ProjectIntent enum
    if "project_intent" in data and isinstance(data.get("project_intent"), str):
        data["project_intent"] = ProjectIntent(data["project_intent"])
    return BrandMemory(**data)


def _serialize_ai_usage(usage: AIUsage) -> dict:
    d = asdict(usage)
    if d["last_ai_call_at"] is not None:
        d["last_ai_call_at"] = d["last_ai_call_at"].isoformat()
    return d


def _deserialize_ai_usage(data: dict | None) -> AIUsage:
    if data is None:
        return AIUsage()
    last = data.get("last_ai_call_at")
    if last and isinstance(last, str):
        last = datetime.fromisoformat(last)
    else:
        last = None
    return AIUsage(
        planner_calls=data.get("planner_calls", 0),
        generation_calls=data.get("generation_calls", 0),
        last_ai_call_at=last,
    )


def _serialize_site_plan(plan: SitePlan | None) -> dict | None:
    if plan is None:
        return None
    d = {
        "page_title": plan.page_title,
        "meta_description": plan.meta_description,
        "sections": [asdict(s) for s in plan.sections],
    }
    if plan.copy_blocks:
        d["copy_blocks"] = [asdict(cb) for cb in plan.copy_blocks]
    if plan.active_sections:
        d["active_sections"] = plan.active_sections
    if plan.selected_template:
        d["selected_template"] = plan.selected_template
    if plan.image_keywords:
        d["image_keywords"] = plan.image_keywords
    if plan.image_overrides:
        d["image_overrides"] = plan.image_overrides
    return d


def _deserialize_site_plan(data: dict | None) -> SitePlan | None:
    if data is None:
        return None
    sections = [SectionPlan(**s) for s in data.get("sections", [])]
    copy_blocks = [
        CopyBlock(**cb) for cb in data.get("copy_blocks", [])
    ]
    return SitePlan(
        sections=sections,
        page_title=data["page_title"],
        meta_description=data["meta_description"],
        copy_blocks=copy_blocks,
        active_sections=data.get("active_sections", []),
        selected_template=data.get("selected_template", ""),
        image_keywords=data.get("image_keywords", {}),
        image_overrides=data.get("image_overrides", {}),
    )


def _serialize_site_version(sv: SiteVersion | None) -> dict | None:
    if sv is None:
        return None
    return asdict(sv)


def _deserialize_site_version(data: dict | None) -> SiteVersion | None:
    if data is None:
        return None
    return SiteVersion(**data)


def _parse_timestamp(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(val)


# --- User CRUD ---

def get_user(user_id: str) -> User | None:
    result = get_client().table("users").select("*").eq("id", user_id).execute()
    if not result.data:
        return None
    row = result.data[0]

    # Payment disabled during beta — all users get full access
    plan = PlanType.AGENCY

    return User(
        id=row["id"],
        email=row["email"],
        plan=plan,
        full_name=row.get("full_name"),
        avatar_url=row.get("avatar_url"),
    )


def upsert_user(user_id: str, email: str, full_name: str | None = None, avatar_url: str | None = None) -> User:
    """Create or update a user by Supabase auth ID."""
    result = get_client().table("users").select("*").eq("id", user_id).execute()
    if result.data:
        update_data = {"email": email}
        if full_name:
            update_data["full_name"] = full_name
        # avatar_url is stored in session, not DB
        get_client().table("users").update(update_data).eq("id", user_id).execute()
    else:
        user_data = {
            "id": user_id,
            "email": email,
            "plan": PlanType.DRAFTER.value,
        }
        if full_name:
            user_data["full_name"] = full_name
        # avatar_url is stored in session, not DB
        get_client().table("users").insert(user_data).execute()
    return get_user(user_id)


def get_user_by_email(email: str) -> User | None:
    result = get_client().table("users").select("*").eq("email", email).execute()
    if not result.data:
        return None
    row = result.data[0]

    # Payment disabled during beta — all users get full access
    plan = PlanType.AGENCY

    return User(
        id=row["id"],
        email=row["email"],
        plan=plan,
        full_name=row.get("full_name"),
        avatar_url=row.get("avatar_url"),
    )



def update_user_subscription(user_id: str, plan: str, customer_id: str, subscription_id: str, status: str, variant_id: str) -> None:
    """Update user subscription details."""
    get_client().table("users").update({
        "plan": plan,
        "lemon_squeezy_customer_id": customer_id,
        "lemon_squeezy_subscription_id": subscription_id,
        "subscription_status": status,
        "variant_id": variant_id,
    }).eq("id", user_id).execute()


# --- Project CRUD ---

def _row_to_project(row: dict) -> Project:
    return Project(
        id=row["id"],
        user_id=row["user_id"],
        state=ProjectState(row["state"]),
        brand_memory=_deserialize_brand_memory(row.get("brand_memory")),
        ai_usage=_deserialize_ai_usage(row.get("ai_usage")),
        site_plan=_deserialize_site_plan(row.get("site_plan")),
        site_version=_deserialize_site_version(row.get("site_version")),
        template_id=row.get("template_id"),
        created_at=_parse_timestamp(row.get("created_at")),
        updated_at=_parse_timestamp(row.get("updated_at")) or _parse_timestamp(row["created_at"]),
        published_at=_parse_timestamp(row.get("published_at")),
    )


def get_project(project_id: str) -> Project | None:
    if not project_id:
        return None
    result = get_client().table("projects").select("*").eq("id", project_id).execute()
    if not result.data:
        return None
    return _row_to_project(result.data[0])


def get_projects_for_user(user_id: str) -> list[Project]:
    result = get_client().table("projects").select("*").eq("user_id", user_id).order("created_at").execute()
    return [_row_to_project(row) for row in result.data]


def count_projects_for_user(user_id: str) -> int:
    result = get_client().table("projects").select("id", count="exact").eq("user_id", user_id).execute()
    return result.count or 0


def create_project(user_id: str) -> Project:
    row = {
        "user_id": user_id,
        "state": ProjectState.DRAFT.value,
        "ai_usage": _serialize_ai_usage(AIUsage()),
    }
    result = get_client().table("projects").insert(row).execute()
    return _row_to_project(result.data[0])


def save_project(project: Project) -> None:
    data = {
        "state": project.state.value,
        "brand_memory": _serialize_brand_memory(project.brand_memory),
        "ai_usage": _serialize_ai_usage(project.ai_usage),
        "site_plan": _serialize_site_plan(project.site_plan),
        "site_version": _serialize_site_version(project.site_version),
        "template_id": project.template_id,
        "published_at": project.published_at.isoformat() if project.published_at else None,
    }
    get_client().table("projects").update(data).eq("id", project.id).execute()


def update_project_trial(project_id: str, trial_ends_at: datetime, is_paused: bool = False) -> None:
    get_client().table("projects").update({
        "trial_ends_at": trial_ends_at.isoformat(),
        "is_paused": is_paused,
    }).eq("id", project_id).execute()


def get_project_row(project_id: str) -> dict | None:
    """Get raw project row (includes trial_ends_at, is_paused)."""
    if not project_id:
        return None
    result = get_client().table("projects").select("*").eq("id", project_id).execute()
    if not result.data:
        return None
    return result.data[0]


def delete_project(project_id: str) -> None:
    """Delete a project and its published sites by ID."""
    client = get_client()
    client.table("published_sites").delete().eq("project_id", project_id).execute()
    client.table("projects").delete().eq("id", project_id).execute()


def set_project_paused(project_id: str, paused: bool) -> None:
    get_client().table("projects").update({"is_paused": paused}).eq("id", project_id).execute()


# --- Published Sites ---

def save_published_site(
    project_id: str,
    version: int,
    storage_path: str,
    public_url: str,
    html_content: str,
    css_content: str,
) -> None:
    get_client().table("published_sites").insert({
        "project_id": project_id,
        "version": version,
        "storage_path": storage_path,
        "public_url": public_url,
        "html_hash": hashlib.sha256(html_content.encode()).hexdigest(),
        "css_hash": hashlib.sha256(css_content.encode()).hexdigest(),
    }).execute()


def get_latest_published_site(project_id: str) -> dict | None:
    if not project_id:
        return None
    result = (
        get_client()
        .table("published_sites")
        .select("*")
        .eq("project_id", project_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0]
