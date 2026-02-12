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
from core.models.brand_memory import BrandMemory
from core.models.ai_usage import AIUsage
from core.models.site_version import SiteVersion
from core.ai.schemas import SitePlan, SectionPlan
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
    return asdict(bm)


def _deserialize_brand_memory(data: dict | None) -> BrandMemory | None:
    if data is None:
        return None
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
    return {
        "page_title": plan.page_title,
        "meta_description": plan.meta_description,
        "sections": [asdict(s) for s in plan.sections],
    }


def _deserialize_site_plan(data: dict | None) -> SitePlan | None:
    if data is None:
        return None
    sections = [SectionPlan(**s) for s in data.get("sections", [])]
    return SitePlan(
        sections=sections,
        page_title=data["page_title"],
        meta_description=data["meta_description"],
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
    return User(
        id=row["id"],
        email=row["email"],
        plan=PlanType(row["plan"]),
    )


def get_user_by_email(email: str) -> User | None:
    result = get_client().table("users").select("*").eq("email", email).execute()
    if not result.data:
        return None
    row = result.data[0]
    return User(
        id=row["id"],
        email=row["email"],
        plan=PlanType(row["plan"]),
    )


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
        created_at=_parse_timestamp(row.get("created_at")),
        published_at=_parse_timestamp(row.get("published_at")),
    )


def get_project(project_id: str) -> Project | None:
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
    result = get_client().table("projects").select("*").eq("id", project_id).execute()
    if not result.data:
        return None
    return result.data[0]


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
