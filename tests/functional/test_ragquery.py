import os
from unittest.mock import ANY, MagicMock, patch

import pytest

from finrobot.functional.ragquery import rag_database_earnings_call, rag_database_sec


@patch("finrobot.functional.ragquery.get_data")
@patch("finrobot.functional.ragquery.SentenceTransformerEmbeddings")
@patch("finrobot.functional.ragquery.Chroma")
@patch("finrobot.functional.ragquery.RecursiveCharacterTextSplitter")
def test_rag_database_earnings_call(mock_splitter_cls, mock_chroma, mock_emb, mock_get_data) -> None:
    # Setup mocks
    mock_docs = [MagicMock()]
    mock_get_data.return_value = (
        mock_docs,
        ["Q1", "Q2", "Q3", "Q4"],  # quarter vals
        ["Speaker1"],  # Q1 speakers
        ["Speaker2"],  # Q2
        ["Speaker3"],  # Q3
        ["Speaker4"],  # Q4
    )

    mock_splitter = mock_splitter_cls.return_value
    mock_splitter.split_documents.return_value = ["doc1", "doc2"]

    mock_db = MagicMock()
    mock_chroma.from_documents.return_value = mock_db

    # Run function
    query_func, quarters, speaker_dict = rag_database_earnings_call("AAPL", "2023")

    assert quarters == ["Q1", "Q2", "Q3", "Q4"]
    assert "Q1" in speaker_dict

    # Test query function logic
    # Mock similarity search results
    doc1 = MagicMock()
    doc1.metadata = {"speaker": "Speaker1", "quarter": "Q1"}
    doc1.page_content = "Transcript text"
    mock_db.similarity_search.return_value = [doc1]

    result = query_func("What did Speaker1 say about revenue?", "Q1")
    assert "Speaker1: Transcript text" in result

    # Check if similarity_search was called with filter
    mock_db.similarity_search.assert_called()
    call_args = mock_db.similarity_search.call_args
    # call_args[1] is kwargs
    assert call_args[1].get("start_filter") is not None or call_args[1].get("filter") is not None


@patch("finrobot.functional.ragquery.get_data")
@patch("finrobot.functional.ragquery.SentenceTransformerEmbeddings")
@patch("finrobot.functional.ragquery.Chroma")
@patch("finrobot.functional.ragquery.RecursiveCharacterTextSplitter")
def test_rag_database_sec_unstructured(mock_splitter_cls, mock_chroma, mock_emb, mock_get_data) -> None:
    mock_get_data.return_value = ([MagicMock()], ["10-K", "10-Q"])

    mock_db = MagicMock()
    mock_chroma.from_documents.return_value = mock_db

    query_func, forms = rag_database_sec("AAPL", "2023", FROM_MARKDOWN=False)

    assert forms == ["10-K", "10-Q"]

    # Test query
    doc1 = MagicMock()
    doc1.metadata = {"section_name": "Item 1", "form_name": "10-K"}
    doc1.page_content = "Business description"
    mock_db.similarity_search.return_value = [doc1]

    result = query_func("What is the business?", "10-K")
    assert "Item 1: Business description" in result


@patch("finrobot.functional.ragquery.get_data")
@patch("finrobot.functional.ragquery.SentenceTransformerEmbeddings")
@patch("finrobot.functional.ragquery.Chroma")
@patch("finrobot.functional.ragquery.MarkdownHeaderTextSplitter")
@patch("os.listdir")
@patch("builtins.open")
def test_rag_database_sec_markdown(
    mock_open, mock_listdir, mock_splitter_cls, mock_chroma, mock_emb, mock_get_data
) -> None:
    # Setup mocks for markdown path
    mock_get_data.return_value = ([], ["10-K"])  # Dummy return for first call

    mock_listdir.side_effect = [
        ["10-K"],  # First call for ticker-year dir
        # No, wait, ragquery iterates: for md_dirs in os.listdir(...)
        # So we mock listdir to return ["10-K"] folder
    ]

    # Mock file read
    mock_f = MagicMock()
    mock_f.read.return_value = "# Header 1\nContent"
    mock_open.return_value.__enter__.return_value = mock_f

    mock_splitter = mock_splitter_cls.return_value
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_doc.page_content = "Content"
    mock_splitter.split_text.return_value = [mock_doc]

    mock_db = MagicMock()
    mock_chroma.from_documents.return_value = mock_db
    mock_db.similarity_search.return_value = [mock_doc]

    query_func, forms = rag_database_sec("AAPL", "2023", FROM_MARKDOWN=True)

    # Test query
    result = query_func("query", "10-K")
    assert "Content" in result
