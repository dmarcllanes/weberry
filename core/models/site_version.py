from dataclasses import dataclass


@dataclass
class SiteVersion:
    html: str
    css: str
    version: int = 1
    is_published: bool = False
