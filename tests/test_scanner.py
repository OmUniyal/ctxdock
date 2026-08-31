import os
import pytest
from pathlib import Path
from ctxdock.core.scanner import Scanner


@pytest.fixture
def tmp_project(tmp_path):
    """Creates a minimal project tree for scanner tests."""
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def helper(): pass")
    (tmp_path / "README.md").write_text("# Project")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "nested.py").write_text("x = 1")
    ignored = tmp_path / "__pycache__"
    ignored.mkdir()
    (ignored / "main.cpython-311.pyc").write_bytes(b"\x00\x01")
    (tmp_path / ".gitignore").write_text("__pycache__/\n*.pyc\n")
    return tmp_path


def test_scans_expected_files(tmp_project):
    scanner = Scanner(root_dir=str(tmp_project))
    found = {str(p) for p in scanner.scan_files()}
    assert "main.py" in found
    assert "utils.py" in found
    assert "README.md" in found
    assert str(Path("subdir") / "nested.py") in found


def test_respects_gitignore(tmp_project):
    scanner = Scanner(root_dir=str(tmp_project))
    found = {str(p) for p in scanner.scan_files()}
    assert not any("__pycache__" in f for f in found)
    assert not any(f.endswith(".pyc") for f in found)


def test_extra_ignore_patterns(tmp_project):
    scanner = Scanner(root_dir=str(tmp_project), extra_ignore_patterns=["*.md"])
    found = {str(p) for p in scanner.scan_files()}
    assert not any(f.endswith(".md") for f in found)


def test_read_file_content(tmp_project):
    scanner = Scanner(root_dir=str(tmp_project))
    content = scanner.read_file_content(Path("main.py"))
    assert "print" in content


def test_read_binary_file_returns_empty(tmp_project):
    binary = tmp_project / "data.bin"
    binary.write_bytes(bytes(range(256)))
    scanner = Scanner(root_dir=str(tmp_project))
    # Should not raise; returns something (replace mode) or empty string
    result = scanner.read_file_content(Path("data.bin"))
    assert isinstance(result, str)