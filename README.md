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

## Quick Start

### Installation

```powershell
pip install -e .

# Pack full context with interactive or default settings
ctxdock

# Compress function bodies and include git diff
ctxdock --compress signatures --git-diff -p "Refactor database connection pooling."
```

## License
MIT