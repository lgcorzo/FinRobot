import json
import os
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("torch")

from finrobot.data_access.data_source.marker_sec_src.pdf_to_md import run_marker
from finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel import (
    process_single_pdf,
    run_marker_mp,
    worker_exit,
    worker_init,
)


@pytest.fixture
def mock_settings() -> None:
    with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.settings") as mock:
        mock.CUDA = False
        mock.INFERENCE_RAM = 100
        mock.VRAM_PER_TASK = 10
        yield mock


def test_run_marker(tmp_path) -> None:  # type: ignore[no-untyped-def]
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "test1.pdf").write_text("dummy")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md.load_all_models") as mock_load:
        with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md.convert_single_pdf") as mock_convert:
            with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md.save_markdown") as mock_save:
                mock_load.return_value = ["model1"]
                mock_convert.return_value = ("text", {}, {})
                run_marker(str(input_dir), str(output_dir))
                mock_convert.assert_called_once()


def test_run_marker_mp_complex(mock_settings, tmp_path) -> None:  # type: ignore[no-untyped-def]
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "doc1.pdf").write_text("d")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    meta_file = tmp_path / "meta.json"
    meta_file.write_text('{"doc1.pdf": {"a": 1}}')

    with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.load_all_models") as mock_load:
        with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.mp.Pool") as mock_pool:
            mock_pool_instance = mock_pool.return_value
            mock_pool_instance.__enter__.return_value = mock_pool_instance
            mock_pool_instance.imap.return_value = []

            # Mock set_start_method to avoid RuntimeError
            with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.mp.set_start_method"):
                run_marker_mp(
                    str(in_dir),
                    str(out_dir),
                    max_files=1,
                    metadata_file=str(meta_file),
                    inference_ram=200,
                    vram_per_task=20,
                    workers=2,
                )
            mock_load.assert_called_once()


def test_run_marker_mp_cuda(mock_settings, tmp_path) -> None:  # type: ignore[no-untyped-def]
    mock_settings.CUDA = True
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "doc.pdf").write_text("d")
    with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.load_all_models") as mock_load:
        model = MagicMock()
        model.device.type = "cuda"
        mock_load.return_value = [model]
        with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.mp.Pool"):
            with patch("finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.mp.set_start_method"):
                run_marker_mp(str(in_dir), str(tmp_path / "out"), inference_ram=100, vram_per_task=10)
                model.share_memory.assert_called_once()


def test_process_single_pdf_edge_cases(tmp_path) -> None:  # type: ignore[no-untyped-def]
    filepath = str(tmp_path / "test.pdf")
    txt_path = str(tmp_path / "test.txt")
    out_folder = str(tmp_path / "out")

    with patch(
        "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.markdown_exists",
        side_effect=[True, False, False, False, False],
    ):
        # exists
        process_single_pdf((filepath, out_folder, {}, None))
        # not pdf
        process_single_pdf((txt_path, out_folder, {}, None))
        # min_length other
        with patch(
            "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.find_filetype", return_value="other"
        ):
            process_single_pdf((filepath, out_folder, {}, 100))
        # min_length too short
        with patch(
            "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.find_filetype", return_value="pdf"
        ):
            with patch(
                "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.get_length_of_text", return_value=50
            ):
                process_single_pdf((filepath, out_folder, {}, 100))
        # exception
        with patch(
            "finrobot.data_access.data_source.marker_sec_src.pdf_to_md_parallel.convert_single_pdf",
            side_effect=Exception("Error"),
        ):
            process_single_pdf((filepath, out_folder, {}, None))
