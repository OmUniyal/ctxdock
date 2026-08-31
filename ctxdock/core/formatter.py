"""
ctxdock.core.formatter
----------------------
Builds structured XML context payloads from packed file data.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileEntry:
    path: str
    content: str
    tokens: int
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