"""
ctxdock.cli
-----------
Click-based command-line entry point.
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

from ctxdock.config import Config
from ctxdock.core.packer import Packer
from ctxdock.core.formatter import ContextPayload
from ctxdock.formatters.xml_formatter import XMLFormatter

console = Console(stderr=True)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--file", "files",
    multiple=True,
    type=click.Path(exists=True, dir_okay=False),
    metavar="PATH",
    help="Pack specific file(s) instead of scanning the directory. Repeatable.",
)
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
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview token usage and compression savings without producing output.",
)
def main(directory, files, compress, git_diff, prompt, budget, no_sanitize, no_copy, output, dry_run):
    """
    ctxdock — local-first LLM context packing.

    Scans DIRECTORY (default: current dir), compresses and sanitises source
    files, and emits a token-optimised XML payload ready for your LLM.

    Use --file to target specific files instead of scanning the whole directory.
    """
    config = Config(
        token_budget=budget,
        compress_mode=compress,
        include_git_diff=git_diff,
        sanitize_secrets=not no_sanitize,
        dry_run=dry_run,
    )

    # Resolve explicit files relative to cwd so packer can relativise them.
    explicit_files = [Path(f).resolve() for f in files] if files else None

    with console.status("[bold cyan]Scanning and packing…", spinner="dots"):
        packer = Packer(config=config, root_dir=directory)
        payload = packer.pack(prompt=prompt, files=explicit_files)

    if dry_run:
        _print_dry_run(payload)
        return

    _print_summary(payload, config)

    formatter = XMLFormatter()
    xml_output = formatter.format_from_payload(payload)

    if output:
        Path(output).write_text(xml_output, encoding="utf-8")
        console.print(f"[green]✓[/green] Written to [bold]{output}[/bold]")
        return

    if not no_copy:
        _copy_to_clipboard(xml_output)
    else:
        click.echo(xml_output)


def _print_dry_run(payload: ContextPayload) -> None:
    """Prints a per-file compression breakdown without emitting any output."""
    console.print()
    console.print("[bold cyan]Dry run — no output produced[/bold cyan]")
    console.print()

    table = Table(box=box.ROUNDED, highlight=True, show_lines=False)
    table.add_column("File", style="dim", no_wrap=False)
    table.add_column("Original", justify="right")
    table.add_column("Packed", justify="right")
    table.add_column("Saved", justify="right")
    table.add_column("%", justify="right")

    total_original = 0
    total_packed = 0

    for entry in payload.files:
        original = entry.original_tokens if entry.compressed else entry.tokens
        packed = entry.tokens
        saved = original - packed
        pct = (saved / original * 100) if original > 0 else 0.0

        total_original += original
        total_packed += packed

        saved_str = f"[green]-{saved:,}[/green]" if saved > 0 else "[dim]—[/dim]"
        pct_str = f"[green]{pct:.0f}%[/green]" if saved > 0 else "[dim]—[/dim]"

        if entry.truncated:
            file_label = f"{entry.path} [yellow][truncated][/yellow]"
        elif entry.compressed:
            file_label = f"{entry.path} [cyan][compressed][/cyan]"
        else:
            file_label = entry.path

        table.add_row(file_label, f"{original:,}", f"{packed:,}", saved_str, pct_str)

    total_saved = total_original - total_packed
    total_pct = (total_saved / total_original * 100) if total_original > 0 else 0.0
    table.add_section()
    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{total_original:,}[/bold]",
        f"[bold]{total_packed:,}[/bold]",
        f"[bold green]-{total_saved:,}[/bold green]",
        f"[bold green]{total_pct:.0f}%[/bold green]",
    )

    console.print(table)

    if payload.skipped_files:
        console.print(
            f"\n[yellow]![/yellow] {len(payload.skipped_files)} file(s) would be "
            "skipped (budget exhausted)"
        )

    console.print()


def _print_summary(payload: ContextPayload, config: Config) -> None:
    pct = payload.total_tokens / payload.token_budget * 100
    bar_filled = int(pct / 5)
    bar = f"[{'█' * bar_filled}{'░' * (20 - bar_filled)}] {pct:.1f}%"

    table = Table(box=box.ROUNDED, show_header=False, padding=(0, 1), highlight=True)
    table.add_column(style="bold cyan", no_wrap=True)
    table.add_column()

    table.add_row("Project",       payload.project_name)
    table.add_row("Files packed",  str(len(payload.files)))
    if payload.skipped_files:
        table.add_row("Files skipped", f"[yellow]{len(payload.skipped_files)}[/yellow] (budget exhausted)")
    table.add_row("Token usage",   f"{payload.total_tokens:,} / {payload.token_budget:,}  {bar}")
    table.add_row("Compress mode", payload.compress_mode)
    table.add_row("Redaction",     "[green]on[/green]" if config.sanitize_secrets else "[dim]off[/dim]")
    if payload.git_diff:
        table.add_row("Git diff",  "[green]included[/green]")

    console.print()
    console.print(table)
    console.print()


def _copy_to_clipboard(text: str) -> None:
    try:
        import pyperclip
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