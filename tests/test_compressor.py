import pytest
from ctxdock.core.compressor import Compressor


@pytest.fixture
def compressor():
    return Compressor()


SIMPLE_FUNCTION = """\
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""

ASYNC_FUNCTION = """\
async def fetch(url: str) -> str:
    response = await client.get(url)
    return response.text
"""

CLASS_WITH_METHODS = """\
class Greeter:
    def __init__(self, name: str):
        self.name = name

    def greet(self) -> str:
        return f"Hello, {self.name}"
"""


def test_compress_python_strips_function_body(compressor):
    result = compressor.compress_python(SIMPLE_FUNCTION)
    assert "return a + b" not in result
    assert "def add(a, b)" in result


def test_compress_python_strips_docstring(compressor):
    result = compressor.compress_python(SIMPLE_FUNCTION)
    assert "Add two numbers" not in result


def test_compress_python_async_function(compressor):
    result = compressor.compress_python(ASYNC_FUNCTION)
    assert "await client.get" not in result
    assert "async def fetch" in result


def test_compress_python_class_methods(compressor):
    result = compressor.compress_python(CLASS_WITH_METHODS)
    assert 'f"Hello, {self.name}"' not in result
    assert "class Greeter" in result
    assert "def greet" in result


def test_compress_python_invalid_syntax_returns_original(compressor):
    bad_code = "def foo(:\n    pass"
    assert compressor.compress_python(bad_code) == bad_code


def test_compress_mode_none_returns_original(compressor):
    result = compressor.compress(SIMPLE_FUNCTION, ".py", mode="none")
    assert result == SIMPLE_FUNCTION


def test_compress_non_python_file_returns_original(compressor):
    js_code = "function foo() { return 42; }"
    result = compressor.compress(js_code, ".js", mode="signatures")
    assert result == js_code


def test_compress_empty_string(compressor):
    assert compressor.compress("", ".py", mode="signatures") == ""