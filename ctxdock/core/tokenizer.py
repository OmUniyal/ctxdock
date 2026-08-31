"""
ctxdock.core.tokenizer
----------------------
Handles token estimation and counting using tiktoken.
"""

import tiktoken


class Tokenizer:
    """Estimates and counts tokens for given text payloads."""

    def __init__(self, model_name: str = "cl100k_base"):
        """
        Initialize the tokenizer.
        Default encoding uses 'cl100k_base' (used by GPT-4, Claude approximations, etc.).
        """
        try:
            self.encoder = tiktoken.get_encoding(model_name)
        except ValueError:
            # Fallback if an invalid encoding name is provided
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Returns the exact number of tokens in a string."""
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def truncate_to_budget(self, text: str, max_tokens: int) -> str:
        """Truncates text to ensure it stays within a specified token limit."""
        tokens = self.encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoder.decode(truncated_tokens)