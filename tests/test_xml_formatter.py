import pytest
from ctxdock.formatters.xml_formatter import XMLFormatter
from ctxdock.core.formatter import ContextPayload, FileEntry


@pytest.fixture
def formatter():
    return XMLFormatter()


@pytest.fixture
def sample_payload():
    return ContextPayload(
        project_name="myproject",
        files=[
            FileEntry(path="main.py", content="print('hi')", tokens=5),
            FileEntry(path="utils.py", content="def foo(): ...", tokens=8, compressed=True),
        ],
        total_tokens=313,
        token_budget=100_000,
        compress_mode="signatures",
        prompt="Refactor the code.",
        git_diff="diff --git a/main.py ...",
        skipped_files=["large_file.py"],
    )


# --- format_payload (original method) ---

def test_format_payload_contains_context_tag(formatter):
    result = formatter.format_payload({"a.py": "x = 1"})
    assert "<context>" in result
    assert "</context>" in result


def test_format_payload_includes_file(formatter):
    result = formatter.format_payload({"a.py": "x = 1"})
    assert 'path="a.py"' in result
    assert "x = 1" in result


def test_format_payload_includes_prompt_outside_context(formatter):
    result = formatter.format_payload({}, user_prompt="Do the thing")
    ctx_end = result.index("</context>")
    prompt_start = result.index("<user_instruction>")
    assert prompt_start > ctx_end


def test_format_payload_omits_prompt_when_none(formatter):
    result = formatter.format_payload({"a.py": "x = 1"})
    assert "<user_instruction>" not in result


def test_format_payload_includes_git_diff(formatter):
    result = formatter.format_payload({}, git_diff="diff --git ...")
    assert "<git_diff>" in result
    assert "diff --git" in result


def test_format_payload_token_count(formatter):
    result = formatter.format_payload({}, total_tokens=42)
    assert "<total_tokens>42</total_tokens>" in result


# --- format_from_payload ---

def test_format_from_payload_structure(formatter, sample_payload):
    result = formatter.format_from_payload(sample_payload)
    assert "<context>" in result
    assert "</context>" in result


def test_format_from_payload_compressed_attr(formatter, sample_payload):
    result = formatter.format_from_payload(sample_payload)
    assert 'compressed="true"' in result


def test_format_from_payload_skipped_files(formatter, sample_payload):
    result = formatter.format_from_payload(sample_payload)
    assert "<skipped_files>" in result
    assert 'path="large_file.py"' in result


def test_format_from_payload_prompt_outside_context(formatter, sample_payload):
    result = formatter.format_from_payload(sample_payload)
    ctx_end = result.index("</context>")
    prompt_start = result.index("<user_instruction>")
    assert prompt_start > ctx_end


def test_format_from_payload_git_diff(formatter, sample_payload):
    result = formatter.format_from_payload(sample_payload)
    assert "<git_diff>" in result


def test_format_from_payload_no_skipped_files(formatter):
    payload = ContextPayload(
        project_name="x", files=[], total_tokens=0,
        token_budget=1000, compress_mode="none",
    )
    result = formatter.format_from_payload(payload)
    assert "<skipped_files>" not in result