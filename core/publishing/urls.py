from config.settings import SUPABASE_URL, SUPABASE_STORAGE_BUCKET


def get_storage_path(project_id: str, version: int) -> str:
    return f"{project_id}/v{version}/index.html"


def get_public_url(project_id: str, version: int) -> str:
    path = get_storage_path(project_id, version)
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{path}"
