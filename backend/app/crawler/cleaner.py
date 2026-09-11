import re
import unicodedata
from typing import List


class ContentCleaner:
    """Sanitizes extracted webpage text while preserving semantic structure."""

    BOILERPLATE_PATTERNS = [
        re.compile(r"(?i)\b(all rights reserved|terms of service|privacy policy|cookie settings)\b.*"),
        re.compile(r"(?i)\b(click here to subscribe|sign up for our newsletter|follow us on)\b.*"),
        re.compile(r"(?i)\b(advertisement|sponsored content|promoted post)\b.*"),
        re.compile(r"(?i)\b(share on facebook|share on twitter|share on linkedin)\b.*"),
    ]

    @classmethod
    def clean(cls, raw_text: str) -> str:
        if not raw_text:
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", raw_text)

        # 2. Split into lines
        lines = normalized.splitlines()
        cleaned_lines: List[str] = []
        seen_lines = set()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                if cleaned_lines and cleaned_lines[-1] != "":
                    cleaned_lines.append("")
                continue

            # Remove obvious boilerplate lines
            if any(p.search(line_str) for p in cls.BOILERPLATE_PATTERNS):
                continue

            # Skip short duplicate repeated lines (e.g. repeated site navigation items)
            if len(line_str) < 40:
                line_lower = line_str.lower()
                if line_lower in seen_lines:
                    continue
                seen_lines.add(line_lower)

            # Preserve markdown-style headings (# ... or ## ...)
            # Normalize whitespace within the line
            line_str = re.sub(r"[ \t]+", " ", line_str)
            cleaned_lines.append(line_str)

        result = "\n".join(cleaned_lines)
        # Collapse multiple empty lines into at most two
        result = re.sub(r"\n{3,}", "\n\n", result)
        return result.strip()
