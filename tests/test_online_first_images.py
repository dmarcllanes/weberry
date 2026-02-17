
import sys
import os

# Ensure current directory is in path (assuming running from project root)
sys.path.append(os.getcwd())

from core.ai.template_renderer import render_template
from core.models.brand_memory import BrandMemory, ProjectIntent
from core.ai.schemas import SitePlan, SectionPlan, CopyBlock

def test_online_first_images_travel():
    # 1. Setup Mock Data
    memory = BrandMemory(
        business_name="TestTravel",
        primary_goal="Bookings",
        website_type="Travel Agency",
        project_intent=ProjectIntent.VALIDATION,
        description="A great travel agency.",
        services=["Tours", "Flights"],
        contact_email="test@test.com",
        contact_phone="1234567890",
        address="123 Test St",
        labeled_assets=[] # No user assets
    )

    plan = SitePlan(
        sections=[SectionPlan(id="home", title="Home", purpose="intro", content_notes="")],
        page_title="Test Travel Site",
        meta_description="Best travel site.",
        selected_template="travel",
        active_sections=["home", "about", "tour", "destination"],
        copy_blocks=[
            CopyBlock("hero_headline", "Explore the World"),
            CopyBlock("hero_description", "Best tours available.")
        ],
        image_keywords={
            "hero_image": "mounatin landscape",
            "about_image": "happy traveler",
            "tour_image_1": "forest adventure"
        }
    )

    # 2. Render Template
    # We use "travel" template which we know exists.
    site_version = render_template("travel", plan, memory)
    
    # 3. Assertions
    html = site_version.html
    
    # Check if the Unsplash URL is present for hero_image
    # The URL format in renderer is: https://source.unsplash.com/featured/{size}/?{keyword}&sig=...
    # We check for the keyword and base URL.
    assert "https://source.unsplash.com/featured/" in html, "Unsplash base URL not found"
    assert "mounatin landscape" in html, "Hero image keyword not found in HTML"
    assert "happy traveler" in html, "About image keyword not found in HTML"
    
    # Check if Jinja variables were replaced
    assert "Explore the World" in html, "Headline not found"
    
    print("Test Passed: Online-First images render correctly with Unsplash URLs.")

if __name__ == "__main__":
    test_online_first_images_travel()
