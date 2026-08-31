"""
ctxdock.core.sanitizer
----------------------
Scans and redacts sensitive information (API keys, secrets, passwords)
from text before packaging prompt payloads.
"""

import re
from typing import List, Tuple


COMMON_SECRET_PATTERNS: List[Tuple[str, str]] = [
    # AWS Access Key
    (r"(?i)(AKIA[0-9A-Z]{16})", "[REDACTED_AWS_ACCESS_KEY]"),
    # Generic API Keys / Tokens (Bearer, Secret, API, Auth)
    (r"(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{16,})['\"]?", r"\1: [REDACTED_SECRET]"),
    # Connection Strings / Database URLs
    (r"(?i)(postgres|postgresql|mysql|mongodb|redis)://([^:]+):([^@]+)@", r"\1://\2:[REDACTED_PASSWORD]@"),
    # Private Keys
    (r"-----BEGIN (RSA|EC|PGP|OPENSSH) PRIVATE KEY-----[\s\S]*?-----END \1 PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
    # GitHub Tokens
    (r"gh[pousr]_[a-zA-Z0-9]{36,}", "[REDACTED_GITHUB_TOKEN]"),
    # OpenAI / Anthropic Keys
    (r"sk-[a-zA-Z0-9]{32,}", "[REDACTED_OPENAI_KEY]"),
    (r"sk-ant-[a-zA-Z0-9]{32,}", "[REDACTED_ANTHROPIC_KEY]"),
]


class Sanitizer:
    """Scans and sanitizes strings to prevent credential leaks."""

    def __init__(self, patterns: List[Tuple[str, str]] = None):
        self.patterns = patterns if patterns is not None else COMMON_SECRET_PATTERNS

    def sanitize(self, text: str) -> str:
        """
        Replaces detected secrets with safety placeholders.
        """
        if not text:
            return ""

        sanitized_text = text
        for pattern, replacement in self.patterns:
            sanitized_text = re.sub(pattern, replacement, sanitized_text)

        return sanitized_text