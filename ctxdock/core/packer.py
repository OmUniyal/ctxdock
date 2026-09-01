"""
ctxdock.core.packer
-------------------
Orchestrates the full context-packing pipeline: scan → sanitize →
compress → budget → assemble payload.
"""

import subprocess
from pathlib import Path
from typing import List, Optional

from ctxdock.config import Config
from ctxdock.core.scanner import Scanner
from ctxdock.core.compressor import Compressor
from ctxdock.core.sanitizer import Sanitizer
from ctxdock.core.tokenizer import Tokenizer
from ctxdock.core.formatter import ContextPayload, FileEntry

_XML_OVERHEAD_TOKENS = 300


class Packer:
    """Runs the full ctxdock pipeline and returns a ContextPayload."""

    def __init__(self, config: Config, root_dir: str = "."):
        self.config = config
        self.root_dir = Path(root_dir).resolve()
        self.scanner = Scanner(
            root_dir=str(self.root_dir),
            extra_ignore_patterns=config.ignore_patterns,
        )
        self.compressor = Compressor()
        self.sanitizer = Sanitizer()
        self.tokenizer = Tokenizer(config.encoding_model)

    def pack(
        self,
        prompt: Optional[str] = None,
        files: Optional[List[Path]] = None,
    ) -> ContextPayload:
        """
        Runs the pipeline and returns the assembled ContextPayload.
        If `files` is provided, only those paths are packed (scanner is skipped).
        Paths in `files` should be absolute or relative to root_dir.
        """
        project_name = self.root_dir.name

        prompt_tokens = self.tokenizer.count_tokens(prompt or "")
        budget = self.config.token_budget - _XML_OVERHEAD_TOKENS - prompt_tokens

        git_diff: Optional[str] = None
        if self.config.include_git_diff:
            git_diff = self._get_git_diff()
            if git_diff:
                budget -= self.tokenizer.count_tokens(git_diff)

        # Resolve which paths to iterate over.
        if files is not None:
            paths = [Path(f).resolve().relative_to(self.root_dir) for f in files]
        else:
            paths = list(self.scanner.scan_files())

        entries: List[FileEntry] = []
        skipped: List[str] = []
        tokens_used = 0

        for rel_path in paths:
            if budget <= 0:
                skipped.append(str(rel_path))
                continue

            content = self.scanner.read_file_content(rel_path)
            if not content:
                continue

            if self.config.sanitize_secrets:
                content = self.sanitizer.sanitize(content)

            original_tokens = self.tokenizer.count_tokens(content)

            compressed = False
            if self.config.compress_mode != "none":
                original_content = content
                content = self.compressor.compress(
                    content, rel_path.suffix, self.config.compress_mode
                )
                compressed = content != original_content

            token_count = self.tokenizer.count_tokens(content)
            truncated = False

            if token_count > budget:
                if budget > 0:
                    content = self.tokenizer.truncate_to_budget(content, budget)
                    token_count = self.tokenizer.count_tokens(content)
                    truncated = True
                else:
                    skipped.append(str(rel_path))
                    continue

            if token_count == 0:
                continue

            entries.append(FileEntry(
                path=str(rel_path),
                content=content,
                tokens=token_count,
                original_tokens=original_tokens,
                compressed=compressed,
                truncated=truncated,
            ))
            budget -= token_count
            tokens_used += token_count

        total_tokens = (
            tokens_used
            + prompt_tokens
            + _XML_OVERHEAD_TOKENS
            + (self.tokenizer.count_tokens(git_diff) if git_diff else 0)
        )

        return ContextPayload(
            project_name=project_name,
            files=entries,
            total_tokens=total_tokens,
            token_budget=self.config.token_budget,
            compress_mode=self.config.compress_mode,
            prompt=prompt or None,
            git_diff=git_diff,
            skipped_files=skipped,
        )

    def _get_git_diff(self) -> Optional[str]:
        """Returns `git diff HEAD` output, or None if unavailable."""
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() or None
        except Exception:
            return None