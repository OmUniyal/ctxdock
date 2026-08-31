import pytest
from ctxdock.core.sanitizer import Sanitizer


@pytest.fixture
def sanitizer():
    return Sanitizer()


def test_redacts_aws_access_key(sanitizer):
    text = "key = AKIAIOSFODNN7EXAMPLE"
    assert "AKIAIOSFODNN7EXAMPLE" not in sanitizer.sanitize(text)
    assert "REDACTED" in sanitizer.sanitize(text)


def test_redacts_openai_key(sanitizer):
    text = "OPENAI_KEY=sk-abcdefghijklmnopqrstuvwxyz123456"
    result = sanitizer.sanitize(text)
    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in result


def test_redacts_anthropic_key(sanitizer):
    text = "key = sk-ant-abcdefghijklmnopqrstuvwxyz1234567890abcd"
    result = sanitizer.sanitize(text)
    assert "sk-ant-" not in result


def test_redacts_github_token(sanitizer):
    text = "token: ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789012"
    result = sanitizer.sanitize(text)
    assert "ghp_" not in result


def test_redacts_database_url_password(sanitizer):
    text = "postgres://user:supersecretpassword@localhost:5432/db"
    result = sanitizer.sanitize(text)
    assert "supersecretpassword" not in result
    assert "user" in result
    assert "localhost" in result


def test_redacts_generic_api_key(sanitizer):
    text = 'api_key = "abcdefghijklmnopqrstuvwxyz123456"'
    result = sanitizer.sanitize(text)
    assert "abcdefghijklmnopqrstuvwxyz123456" not in result


def test_empty_string_returns_empty(sanitizer):
    assert sanitizer.sanitize("") == ""


def test_clean_text_is_unchanged(sanitizer):
    text = "This is a normal comment with no secrets."
    assert sanitizer.sanitize(text) == text


def test_custom_patterns(sanitizer):
    custom = [(r"MYTOKEN-\w+", "[REDACTED_CUSTOM]")]
    s = Sanitizer(patterns=custom)
    result = s.sanitize("auth = MYTOKEN-abc123")
    assert "MYTOKEN-abc123" not in result
    assert "[REDACTED_CUSTOM]" in result