"""
ctxdock.formatters.xml_formatter
--------------------------------
Formats selected project files, git diffs, and prompts into a structured XML payload.
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ctxdock.core.formatter import ContextPayload


class XMLFormatter:
    """Formats bundled context into structured XML for LLMs."""

    def format_payload(
        self,
        files_data: Dict[str, str],
        user_prompt: Optional[str] = None,
        git_diff: Optional[str] = None,
        total_tokens: int = 0,
    ) -> str:
        """
        Assembles all parts into a clean XML prompt block.
        """
        output = []
        output.append("<context>")
        output.append(f"  <meta>")
        output.append(f"    <total_tokens>{total_tokens}</total_tokens>")
        output.append(f"    <file_count>{len(files_data)}</file_count>")
        output.append(f"  </meta>\n")

        if git_diff:
            output.append("  <git_diff>")
            output.append(git_diff.strip())
            output.append("  </git_diff>\n")

        output.append("  <files>")
        for filepath, content in files_data.items():
            output.append(f'    <file path="{filepath}">')
            output.append(content.strip())
            output.append("    </file>")
        output.append("  </files>")
        output.append("</context>\n")

        if user_prompt:
            output.append("<user_instruction>")
            output.append(user_prompt.strip())
            output.append("</user_instruction>")

        return "\n".join(output)

    def format_from_payload(self, payload: "ContextPayload") -> str:
        """
        Renders a ContextPayload into XML, preserving per-file metadata
        (compressed, truncated) and skipped-file reporting.
        """
        output = []
        output.append("<context>")
        output.append("  <meta>")
        output.append(f"    <total_tokens>{payload.total_tokens}</total_tokens>")
        output.append(f"    <token_budget>{payload.token_budget}</token_budget>")
        output.append(f"    <file_count>{len(payload.files)}</file_count>")
        output.append(f"    <compress_mode>{payload.compress_mode}</compress_mode>")
        output.append("  </meta>\n")

        if payload.git_diff:
            output.append("  <git_diff>")
            output.append(payload.git_diff.strip())
            output.append("  </git_diff>\n")

        output.append("  <files>")
        for entry in payload.files:
            attrs = f'path="{entry.path}" tokens="{entry.tokens}"'
            if entry.compressed:
                attrs += ' compressed="true"'
            if entry.truncated:
                attrs += ' truncated="true"'
            output.append(f"    <file {attrs}>")
            output.append(entry.content.strip())
            output.append("    </file>")
        output.append("  </files>")

        if payload.skipped_files:
            output.append("\n  <skipped_files>")
            for path in payload.skipped_files:
                output.append(f'    <file path="{path}"/>')
            output.append("  </skipped_files>")

        output.append("</context>\n")

        if payload.prompt:
            output.append("<user_instruction>")
            output.append(payload.prompt.strip())
            output.append("</user_instruction>")

        return "\n".join(output)