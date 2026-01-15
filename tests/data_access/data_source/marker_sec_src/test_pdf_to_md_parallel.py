import os
from unittest.mock import MagicMock, call, patch

import pytest
from finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel import (
    process_single_pdf,
    run_marker_mp,
)


# Mock dependencies
@pytest.fixture
def mock_dependencies():
    with patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.load_all_models"
    ) as mock_load, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.mp.Pool"
    ) as mock_pool, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.settings"
    ) as mock_settings, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.convert_single_pdf"
    ) as mock_convert, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.save_markdown"
    ) as mock_save, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.markdown_exists"
    ) as mock_exists, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.os.listdir"
    ) as mock_listdir, patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.os.path.isfile"
    ) as mock_isfile:
        mock_settings.CUDA = False
        yield mock_load, mock_pool, mock_settings, mock_convert, mock_save, mock_exists, mock_listdir, mock_isfile


def test_run_marker_mp_basic(mock_dependencies, tmp_path):
    mock_load, mock_pool, mock_settings, mock_convert, mock_save, mock_exists, mock_listdir, mock_isfile = (
        mock_dependencies
    )

    # Setup mocks
    mock_listdir.return_value = ["doc1.pdf"]
    mock_isfile.return_value = True

    # Mock pool context manager
    mock_pool_instance = mock_pool.return_value
    mock_pool_instance.__enter__.return_value = mock_pool_instance
    mock_pool_instance.imap.return_value = []  # Return empty iterator for tqdm

    # Run function
    run_marker_mp("in_dir", "out_dir", workers=1)

    # Assertions
    mock_load.assert_called_once()
    mock_pool.assert_called()
    mock_pool_instance.imap.assert_called()


def test_process_single_pdf(mock_dependencies):
    mock_load, mock_pool, mock_settings, mock_convert, mock_save, mock_exists, mock_listdir, mock_isfile = (
        mock_dependencies
    )

    # Setup for process_single_pdf
    mock_exists.return_value = False
    mock_convert.return_value = ("MarkDown Content", {"image": "data"}, {"meta": "data"})

    args = ("path/to/doc.pdf", "out_dir", {}, None)

    # We need to simulate the worker initialization if global model_refs is used
    # But for unit test we can patch model_refs in the module if needed,
    # OR we assume convert_single_pdf handles the logic and we just verify calls.
    # The global 'model_refs' is set by worker_init. process_single_pdf uses it as argument to convert_single_pdf?
    # No, convert_single_pdf(filepath, model_refs...)

    # We need to set the global model_refs in the module for this test to work without error
    with patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.model_refs", "DUMMY_MODEL_REFS", create=True
    ):
        process_single_pdf(args)

    mock_convert.assert_called_with("path/to/doc.pdf", "DUMMY_MODEL_REFS", metadata={})
    mock_save.assert_called_with("out_dir", "doc.pdf", "MarkDown Content", {"image": "data"}, {"meta": "data"})


def test_process_single_pdf_already_exists(mock_dependencies):
    mock_load, mock_pool, mock_settings, mock_convert, mock_save, mock_exists, mock_listdir, mock_isfile = (
        mock_dependencies
    )
    mock_exists.return_value = True

    args = ("path/to/doc.pdf", "out_dir", {}, None)
    process_single_pdf(args)

    mock_convert.assert_not_called()


def test_process_single_pdf_not_pdf(mock_dependencies):
    # no mock setup needed, just args
    args = ("path/to/doc.txt", "out_dir", {}, None)
    process_single_pdf(args)
    # Implicitly assert no crash and likely no calls to convert (can verify if we had handle)
    # mock_convert is available via fixture
    mock_load, mock_pool, mock_settings, mock_convert, mock_save, mock_exists, mock_listdir, mock_isfile = (
        mock_dependencies
    )
    mock_convert.assert_not_called()
