import pytest
from ctxdock.core.tokenizer import Tokenizer


@pytest.fixture
def tokenizer():
    return Tokenizer()


def test_count_tokens_nonempty(tokenizer):
    assert tokenizer.count_tokens("hello world") > 0


def test_count_tokens_empty(tokenizer):
    assert tokenizer.count_tokens("") == 0


def test_count_tokens_increases_with_length(tokenizer):
    short = tokenizer.count_tokens("hi")
    long = tokenizer.count_tokens("hi " * 100)
    assert long > short


def test_truncate_within_budget_unchanged(tokenizer):
    text = "hello world"
    result = tokenizer.truncate_to_budget(text, max_tokens=100)
    assert result == text


def test_truncate_enforces_budget(tokenizer):
    text = "word " * 200
    result = tokenizer.truncate_to_budget(text, max_tokens=10)
    assert tokenizer.count_tokens(result) <= 10


def test_truncate_result_is_prefix(tokenizer):
    text = "apple banana cherry date elderberry"
    result = tokenizer.truncate_to_budget(text, max_tokens=2)
    assert text.startswith(result)


def test_invalid_encoding_falls_back(tokenizer):
    t = Tokenizer(model_name="not_a_real_encoding")
    assert t.count_tokens("test") > 0