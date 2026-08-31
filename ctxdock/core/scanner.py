"""
ctxdock.core.scanner
--------------------
Traverses directory trees while adhering to ignore patterns (.gitignore).
"""

import os
from pathlib import Path
from typing import List, Generator
import pathspec


class Scanner:
    """Scans and filters files in a directory tree."""

    def __init__(self, root_dir: str = ".", extra_ignore_patterns: List[str] = None):
        self.root_dir = Path(root_dir).resolve()
        self.extra_ignore_patterns = extra_ignore_patterns or []
        self.spec = self._build_pathspec()

    def _build_pathspec(self) -> pathspec.PathSpec:
        """Loads .gitignore patterns and combines them with extra ignore patterns."""
        patterns = list(self.extra_ignore_patterns)

        gitignore_path = self.root_dir / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                patterns.extend(f.readlines())

        return pathspec.PathSpec.from_lines("gitignore", patterns)

    def scan_files(self) -> Generator[Path, None, None]:
        """
        Yields relative paths of valid files, skipping ignored files and directories.
        """
        for root, dirs, files in os.walk(self.root_dir):
            rel_root = Path(root).relative_to(self.root_dir)

            # Filter directories in-place to prevent traversing ignored paths
            dirs[:] = [
                d for d in dirs
                if not self.spec.match_file(str(rel_root / d) + "/")
            ]

            for file in files:
                rel_path = rel_root / file
                if str(rel_path) == ".":
                    rel_path = Path(file)

                if not self.spec.match_file(str(rel_path)):
                    yield rel_path

    def read_file_content(self, relative_path: Path) -> str:
        """Safely reads content of a text file, skipping binary or unreadable files."""
        full_path = self.root_dir / relative_path
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return ""