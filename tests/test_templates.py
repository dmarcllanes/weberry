import unittest
from pathlib import Path
from core.ai.template_loader import list_templates
from core.ai.template_renderer import render_template
from core.ai.schemas import SitePlan, CopyBlock
from core.models.brand_memory import BrandMemory, ProjectIntent
from core.models.site_version import SiteVersion

class TestTemplates(unittest.TestCase):
    def setUp(self):
        self.templates = list_templates()
        self.dummy_memory = BrandMemory(
            business_name="Test Business",
            website_type="Business",
            primary_goal="Growth",
            project_intent=ProjectIntent.VALIDATION
        )
        # Populate dummy plan with all possible blocks to avoid key errors if templates are strict
        # (Though Jinja usually fails gracefully, it's good to provide data)
        self.dummy_plan = SitePlan(
            sections=[],
            page_title="Test Page",
            meta_description="Test Meta",
            copy_blocks=[
                CopyBlock(placeholder_key="hero_headline", content="Hero Headline"),
                CopyBlock(placeholder_key="hero_subheadline", content="Hero Subheadline"),
                CopyBlock(placeholder_key="cta_button_text", content="Click Me"),
                CopyBlock(placeholder_key="about_headline", content="About Us"),
                CopyBlock(placeholder_key="about_description", content="We are great."),
                CopyBlock(placeholder_key="services_headline", content="Our Services"),
                CopyBlock(placeholder_key="portfolio_headline", content="Our Work"),
                CopyBlock(placeholder_key="testimonials_headline", content="Testimonials"),
                CopyBlock(placeholder_key="contact_headline", content="Contact Us"),
            ],
            # Activate all common sections to test all parts of template
            active_sections=["features", "services", "portfolio", "testimonials", "about", "contact"],
            selected_template="", # Will be set in loop
            image_keywords={"hero_image": "business", "hero_bg": "office"}
        )
        
        # Add list data
        self.dummy_plan.copy_blocks.append(CopyBlock(placeholder_key="services_list", content='[{"title": "Service 1", "description": "Desc 1"}, {"title": "Service 2", "description": "Desc 2"}, {"title": "Service 3", "description": "Desc 3"}, {"title": "Service 4", "description": "Desc 4"}]'))
        self.dummy_plan.copy_blocks.append(CopyBlock(placeholder_key="features_list", content='[{"title": "Feature 1", "description": "Desc 1"}, {"title": "Feature 2", "description": "Desc 2"}, {"title": "Feature 3", "description": "Desc 3"}]'))
        self.dummy_plan.copy_blocks.append(CopyBlock(placeholder_key="testimonials_list", content='[{"quote": "Great!", "author": "Alice"}, {"quote": "Super!", "author": "Bob"}]'))

    def test_render_all_templates(self):
        """Ensure all templates render without error."""
        for tmpl in self.templates:
            t_id = tmpl["id"]
            print(f"Testing template: {t_id}")
            
            # Set ID
            self.dummy_plan.selected_template = t_id
            
            try:
                result = render_template(t_id, self.dummy_plan, self.dummy_memory)
                self.assertIsInstance(result, SiteVersion)
                self.assertIn("<!DOCTYPE html>", result.html)
                self.assertIn("Test Business", result.html)
                # Check for critical variables
                self.assertIn("Hero Headline", result.html)
            except Exception as e:
                self.fail(f"Template {t_id} failed to render: {e}")

if __name__ == "__main__":
    unittest.main()
