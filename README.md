# ctxdock

> **Local-first LLM context packing and prompt optimization engine.**

`ctxdock` is a fast, terminal-first utility designed to inspect, compress, and pack project code, git diffs, and developer instructions into token-optimized payloads for Large Language Models.

---

## Key Features

- **Token-Aware Budgeting:** Real-time token estimation using `tiktoken` to fit within model context limits.
- **AST Code Compression:** Strips comments, docstrings, and function bodies for reference-only context.
- **Secret Redaction:** Automatic scanning and sanitization of credentials and sensitive environment variables.
- **Structured XML Output:** Clean, deterministic context formatting designed for optimal LLM retrieval.
- **Clipboard Native:** Direct copy-to-clipboard integration for fast pasting into chat interfaces.

---

## Requirements

- Python 3.10+

---

## Installation

```bash
# Install for use
pip install -e .

# Install with dev dependencies (includes pytest)
pip install -e ".[dev]"
```

---

## Usage

```bash
# Pack current directory with defaults (copies to clipboard)
ctxdock

# Compress function bodies and include git diff
ctxdock --compress signatures --git-diff -p "Refactor database connection pooling."

# Set a custom token budget and write output to a file
ctxdock --budget 32000 -o context.xml

# Disable secret redaction and clipboard copy
ctxdock --no-sanitize --no-copy
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--compress [none\|signatures]` | `none` | Strip function bodies, keep signatures |
| `--git-diff` | off | Append `git diff HEAD` to the payload |
| `-p, --prompt TEXT` | — | Developer instruction to embed |
| `--budget N` | `100000` | Maximum token budget |
| `--no-sanitize` | off | Disable secret redaction |
| `--no-copy` | off | Print to stdout instead of clipboard |
| `-o, --output FILE` | — | Write payload to a file |

---

## Running Tests

```bash
pytest -v
```

---

## License

MIT