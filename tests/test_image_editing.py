
import sys
import os
import pytest
from unittest.mock import patch

# Ensure current directory is in path
sys.path.append(os.getcwd())

from core.models.brand_memory import BrandMemory, ProjectIntent
from core.models.project import Project
from core.models.user import User
from core.ai.schemas import SitePlan, SectionPlan, CopyBlock
from core.state_machine.states import ProjectState
from user_app.services.project_service import rerender_site

def test_image_editing_logic():
    # 1. Setup Data
    user = User(id="test_user", email="test@example.com", paid_credits=1)
    memory = BrandMemory(
        business_name="TestEdit",
        primary_goal="Bookings",
        website_type="Travel Agency",
        project_intent=ProjectIntent.VALIDATION,
        description="A great travel agency.",
        services=["Tours"],
        contact_email="test@test.com"
    )
    
    plan = SitePlan(
        sections=[SectionPlan(id="home", title="Home", purpose="intro", content_notes="")],
        page_title="Test Site",
        meta_description="Desc",
        selected_template="travel",
        active_sections=["home"],
        copy_blocks=[],
        image_keywords={"hero_image": "mountain"},
        image_overrides={}
    )
    
    project = Project(
        id="test_project",
        user_id=user.id,
        state=ProjectState.SITE_GENERATED,
        brand_memory=memory,
        site_plan=plan,
        site_version=None
    )
    
    # 2. Initial Render
    with patch("user_app.services.project_service.db.save_project"):
        rerender_site(project)
    initial_html = project.site_version.html
    
    # Assert initial render uses Unsplash (based on keyword)
    assert "source.unsplash.com" in initial_html
    assert "mountain" in initial_html
    
    # 3. Apply Override
    override_url = "https://example.com/my-custom-image.jpg"
    project.site_plan.image_overrides["hero_image"] = override_url
    
    # 4. Re-render
    with patch("user_app.services.project_service.db.save_project"):
        rerender_site(project)
    updated_html = project.site_version.html
    
    # Assert updated render uses Override URL
    assert override_url in updated_html
    # Unsplash keyword might still be there for other slots or loop variables, 
    # but the specific slot URL should be replaced. 
    # In my template_renderer logic, I inject {slot_name}_url = override_url.
    # Jinja template uses {{ hero_image_url }}.
    
    print("Test Passed: Image override successfully replaced the unsplash URL.")

if __name__ == "__main__":
    test_image_editing_logic()
