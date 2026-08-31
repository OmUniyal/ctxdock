"""
ctxdock.cli
-----------
Click-based command-line entry point.
"""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

from ctxdock.config import Config
from ctxdock.core.packer import Packer
from ctxdock.formatters.xml_formatter import XMLFormatter

formatter = XMLFormatter()
xml_output = formatter.format_from_payload(payload)

console = Console(stderr=True)  # Diagnostics go to stderr; XML payload to stdout.


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--compress",
    type=click.Choice(["none", "signatures"]),
    default="none",
    show_default=True,
    help="Strip function bodies, keeping only signatures.",
)
@click.option(
    "--git-diff",
    is_flag=True,
    default=False,
    help="Append `git diff HEAD` to the context payload.",
)
@click.option(
    "-p", "--prompt",
    default=None,
    metavar="TEXT",
    help="Developer instruction to embed in the payload.",
)
@click.option(
    "--budget",
    default=100_000,
    show_default=True,
    type=int,
    metavar="N",
    help="Maximum token budget for the packed context.",
)
@click.option(
    "--no-sanitize",
    is_flag=True,
    default=False,
    help="Disable automatic secret redaction.",
)
@click.option(
    "--no-copy",
    is_flag=True,
    default=False,
    help="Do not copy output to the clipboard.",
)
@click.option(
    "-o", "--output",
    default=None,
    type=click.Path(dir_okay=False, writable=True),
    help="Write the XML payload to a file instead of stdout.",
)
def main(directory, compress, git_diff, prompt, budget, no_sanitize, no_copy, output):
    """
    ctxdock — local-first LLM context packing.

    Scans DIRECTORY (default: current dir), compresses and sanitises source
    files, and emits a token-optimised XML payload ready for your LLM.
    """
    config = Config(
        token_budget=budget,
        compress_mode=compress,
        include_git_diff=git_diff,
        sanitize_secrets=not no_sanitize,
    )

    with console.status("[bold cyan]Scanning and packing…", spinner="dots"):
        packer = Packer(config=config, root_dir=directory)
        payload = packer.pack(prompt=prompt)

    formatter = Formatter()
    xml_output = formatter.format(payload)

    _print_summary(payload, config)

    if output:
        Path(output).write_text(xml_output, encoding="utf-8")
        console.print(f"[green]✓[/green] Written to [bold]{output}[/bold]")
        return

    if not no_copy:
        _copy_to_clipboard(xml_output)
    else:
        click.echo(xml_output)


def _print_summary(payload, config) -> None:
    pct = payload.total_tokens / payload.token_budget * 100
    bar_filled = int(pct / 5)
    bar = f"[{'█' * bar_filled}{'░' * (20 - bar_filled)}] {pct:.1f}%"

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1), highlight=True)
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()

    table.add_row("Project",        payload.project_name)
    table.add_row("Files packed",   str(len(payload.files)))
    if payload.skipped_files:
        table.add_row("Files skipped", f"[yellow]{len(payload.skipped_files)}[/yellow] (budget exhausted)")
    table.add_row("Token usage",    f"{payload.total_tokens:,} / {payload.token_budget:,}  {bar}")
    table.add_row("Compress mode",  payload.compress_mode)
    table.add_row("Redaction",      "[green]on[/green]" if config.sanitize_secrets else "[dim]off[/dim]")
    if payload.git_diff:
        table.add_row("Git diff",   "[green]included[/green]")

    console.print()
    console.print(table)
    console.print()


def _copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip  # optional dep
        pyperclip.copy(text)
        console.print("[green]✓[/green] Copied to clipboard.")
    except ImportError:
        console.print(
            "[yellow]![/yellow] [dim]Install [bold]pyperclip[/bold] (`pip install pyperclip`) "
            "to enable clipboard copy.[/dim]"
        )
        click.echo(text)
    except Exception as exc:
        console.print(f"[yellow]![/yellow] Clipboard unavailable: {exc}")
        click.echo(text)