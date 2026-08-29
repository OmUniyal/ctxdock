"""
ctxdock.formatters.xml_formatter
--------------------------------
Formats selected project files, git diffs, and prompts into a structured XML payload.
"""

from typing import Dict, Optional


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