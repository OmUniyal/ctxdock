"""
ctxdock.config
--------------
Global configuration settings, default ignore rules, and token budgets.
"""

from dataclasses import dataclass, field
from typing import List


DEFAULT_IGNORE_PATTERNS: List[str] = [
    # VCS & IDEs
    ".git/",
    ".svn/",
    ".hg/",
    ".idea/",
    ".vscode/",
    # Python Cache & Envs
    "__pycache__/",
    "*.py[cod]",
    ".venv/",
    "venv/",
    "env/",
    "*.egg-info/",
    "dist/",
    "build/",
    # Node / Web
    "node_modules/",
    ".next/",
    "build/",
    # OS files
    "Thumbs.db",
    ".DS_Store",
    # Local Logs & Lockfiles
    "*.log",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
]


@dataclass
class Config:
    """Configuration options for context packing."""
    token_budget: int = 100_000
    encoding_model: str = "cl100k_base"
    compress_mode: str = "none"  # Options: 'none', 'signatures'
    include_git_diff: bool = False
    sanitize_secrets: bool = True
    ignore_patterns: List[str] = field(default_factory=lambda: DEFAULT_IGNORE_PATTERNS)


default_config = Config()