"""Load and inspect template manifests from the templates/ directory."""

import json
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


def list_templates() -> list[dict]:
    """Scan templates/*/manifest.json and return all manifests."""
    templates = []
    if not TEMPLATES_DIR.exists():
        return templates
    for manifest_path in sorted(TEMPLATES_DIR.rglob("manifest.json")):
        with open(manifest_path) as f:
            templates.append(json.load(f))
    return templates


def load_template_manifest(template_id: str) -> dict:
    """Load a single template manifest by ID."""
    manifest_path = TEMPLATES_DIR / template_id / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Template '{template_id}' not found")
    with open(manifest_path) as f:
        return json.load(f)


def get_templates_summary() -> str:
    """Formatted summary of all templates for the AI prompt."""
    templates = list_templates()
    if not templates:
        return "No templates available."
    lines = []
    for t in templates:
        optional = ", ".join(t.get("optional_sections", []))
        copy_keys = ", ".join(t.get("copy_keys", []))
        list_keys_data = t.get("list_keys", {})
        list_parts = []
        for list_name, fields in list_keys_data.items():
            list_parts.append(f"{list_name} (fields: {', '.join(fields)})")
        list_keys_str = "; ".join(list_parts) if list_parts else "none"
        lines.append(
            f"- ID: {t['id']}\n"
            f"  Name: {t['name']}\n"
            f"  Intent: {t.get('intent', 'general')}\n"
            f"  Description: {t['description']}\n"
            f"  Optional sections: {optional}\n"
            f"  Required copy keys: {copy_keys}\n"
            f"  List keys: {list_keys_str}"
        )
    return "\n".join(lines)
