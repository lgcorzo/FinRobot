from unittest.mock import MagicMock, mock_open, patch

import pytest
from finrobot.functional.coding import CodingUtils, IPythonUtils


class TestIPythonUtils:
    @patch("finrobot.functional.coding.get_ipython")
    def test_exec_python(self, mock_get_ipython):
        mock_shell = MagicMock()
        mock_get_ipython.return_value = mock_shell

        # Success case
        mock_result = MagicMock()
        mock_result.error_before_exec = None
        mock_result.error_in_exec = None
        mock_result.result = "Success"
        mock_shell.run_cell.return_value = mock_result

        log = IPythonUtils.exec_python("print('hello')")
        assert "Success" in log

        # Error case
        mock_result.error_before_exec = "ErrorBefore"
        mock_result.error_in_exec = "ErrorIn"
        log = IPythonUtils.exec_python("error")
        assert "ErrorBefore" in log
        assert "ErrorIn" in log

    @patch("finrobot.functional.coding.IPythonUtils.exec_python")
    def test_display_image(self, mock_exec):
        mock_exec.return_value = ""  # No error
        res = IPythonUtils.display_image("test.png")
        assert "successfully" in res

        mock_exec.return_value = "Error"
        res = IPythonUtils.display_image("test.png")
        assert "Error" in res


class TestCodingUtils:
    @patch("finrobot.functional.coding.os.listdir")
    def test_list_dir(self, mock_listdir):
        mock_listdir.return_value = ["file1", "file2"]
        res = CodingUtils.list_dir("folder")
        assert "file1" in res
        # Check defaults if needed or just return str

    @patch("builtins.open", new_callable=mock_open, read_data="line1\nline2")
    def test_see_file(self, mock_file):
        res = CodingUtils.see_file("file.txt")
        assert "1:line1" in res
        assert "2:line2" in res

    @patch("builtins.open", new_callable=mock_open, read_data="line1\nline2\nline3")
    def test_modify_code(self, mock_file):
        # Read happens first
        # Then write
        # This is tricky with mock_open because read_data is consumed?
        # modify_code uses r+ mode.

        res = CodingUtils.modify_code("file.py", 2, 2, "new_code")
        assert "Code modified" in res

        # Verify write
        handle = mock_file()
        handle.write.assert_called()
        # We can check check if write content contains new_code
        args = handle.write.call_args[0][0]
        assert "new_code" in args

    @patch("builtins.open", new_callable=mock_open)
    @patch("finrobot.functional.coding.os.makedirs")
    def test_create_file_with_code(self, mock_makedirs, mock_file):
        res = CodingUtils.create_file_with_code("dir/file.py", "print('hello')")
        assert "successfully" in res
        mock_makedirs.assert_called()
        mock_file.assert_called_with("./dir/file.py", "w")
        mock_file().write.assert_called_with("print('hello')")
