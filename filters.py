"""
Keyword and region filtering for job listings.
"""
import config


def matches_keywords(text: str) -> bool:
    if not config.KEYWORDS:
        return True
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in config.KEYWORDS)


def matches_region(text: str) -> bool:
    if not config.REGIONS:
        return True
    text_lower = text.lower()
    return any(region.lower() in text_lower for region in config.REGIONS)


def is_relevant(title: str, description: str = "", location: str = "") -> bool:
    combined = f"{title} {description}"
    return matches_keywords(combined) and matches_region(f"{combined} {location}")
