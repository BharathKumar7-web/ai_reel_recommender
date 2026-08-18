"""
Helper utilities for input sanitization, text formatting, and UI helpers.
"""

import re
import html
from typing import Any, Dict

def sanitize_text_input(text: str) -> str:
    """Sanitizes external untrusted user text against injection and HTML entities."""
    if not isinstance(text, str):
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]*>", "", text)
    # Unescape HTML entities
    clean = html.unescape(clean)
    # Trim excess whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def format_percentage(val: float) -> str:
    """Formats float value as percentage string."""
    return f"{int(round(val * 100))}%"

def truncate_text(text: str, max_chars: int = 120) -> str:
    """Truncates text with ellipsis."""
    if not text:
        return ""
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "..."
