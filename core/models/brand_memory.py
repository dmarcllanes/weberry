from dataclasses import dataclass, field


@dataclass
class BrandMemory:
    business_name: str
    website_type: str
    primary_goal: str
    description: str = ""
    theme: str = "professional"
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"
    contact_email: str = ""
    contact_phone: str = ""
    address: str = ""
    tagline: str = ""
    services: list[str] = field(default_factory=list)
