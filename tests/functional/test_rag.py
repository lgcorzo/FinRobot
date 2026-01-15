"""Tests for functional RAG module."""


class TestRAGFunction:
    """Test suite for RAG functions.

    These tests verify the module can be imported.
    """

    def test_rag_module_import(self):
        """Test that rag module can be imported."""
        from finrobot.functional import rag

        assert rag is not None

    def test_get_rag_function_exists(self):
        """Test that get_rag_function exists."""
        from finrobot.functional.rag import get_rag_function

        assert get_rag_function is not None
        assert callable(get_rag_function)
