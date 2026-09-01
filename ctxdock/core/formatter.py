"""
ctxdock.core.formatter
----------------------
Data structures for assembled context payloads.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileEntry:
    path: str
    content: str
    tokens: int
    original_tokens: int = 0      # pre-compression token count; 0 if not compressed
    compressed: bool = False
    truncated: bool = False


@dataclass
class ContextPayload:
    project_name: str
    files: List[FileEntry]
    total_tokens: int
    token_budget: int
    compress_mode: str
    prompt: Optional[str] = None
    git_diff: Optional[str] = None
    skipped_files: List[str] = field(default_factory=list)