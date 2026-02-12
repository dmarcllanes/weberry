from enum import Enum


class ProjectState(Enum):
    DRAFT = "draft"
    INPUT_READY = "input_ready"
    MEMORY_READY = "memory_ready"
    PLAN_READY = "plan_ready"
    PLAN_APPROVED = "plan_approved"
    SITE_GENERATED = "site_generated"
    PREVIEW = "preview"
    PUBLISHED = "published"
    ERROR = "error"
