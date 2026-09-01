# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- `--dry-run` flag — per-file token breakdown table showing original vs packed
  token counts and compression savings percentage; no output is produced
- `--file` flag — target one or more specific files instead of scanning the
  whole directory; repeatable (`--file a.py --file b.py`)
- `original_tokens` tracked per `FileEntry` to power dry-run compression comparisons
- `dry_run` field added to `Config`

---

## [0.1.0] - 2026-08-31

### Added

- `Compressor` — AST-based Python code compressor that strips function bodies
  and docstrings, retaining only signatures and decorators (`--compress signatures`)
- `Sanitizer` — regex-based secret redaction for AWS keys, OpenAI/Anthropic keys,
  GitHub tokens, database URLs, and generic API key patterns
- `Scanner` — directory traversal with `.gitignore` and custom pattern support
  via `pathspec`
- `Tokenizer` — token counting and budget-aware truncation using `tiktoken`
  (`cl100k_base` encoding by default)
- `Packer` — pipeline orchestrator that wires scan → sanitize → compress →
  budget → assemble into a single `ContextPayload`
- `XMLFormatter` — structured XML output with per-file `compressed` and
  `truncated` attributes, skipped-file reporting, and `<user_instruction>`
  placed after `</context>` for optimal LLM retrieval
- CLI entry point (`ctxdock`) with flags: `--compress`, `--git-diff`,
  `--prompt`, `--budget`, `--no-sanitize`, `--no-copy`, `--output`
- Clipboard-native output via `pyperclip` with graceful degradation
- Rich terminal summary table showing token usage, file count, and redaction
  status
- Unit test suite — 41 tests across all core modules and the XML formatter

### Notes

- Python 3.10+ required (`ast.unparse` dependency)
- Non-Python files are passed through unmodified in `signatures` mode;
  additional language support planned