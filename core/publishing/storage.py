from core.publishing.urls import get_storage_path


def upload_site(storage_client, project_id: str, version: int, rendered_html: str, bucket: str) -> str:
    """
    Upload rendered HTML to object storage.

    Args:
        storage_client: Supabase storage client (injected, core stays framework-agnostic)
        project_id: The project UUID
        version: Site version number
        rendered_html: The fully rendered HTML page (CSS inlined)
        bucket: Storage bucket name

    Returns:
        The storage path of the uploaded file
    """
    path = get_storage_path(project_id, version)
    file_bytes = rendered_html.encode("utf-8")

    storage_client.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": "text/html", "upsert": "true"},
    )

    return path
