import json
import os
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from finrobot.infrastructure.io.files import register_keys_from_json, save_output


class TestFiles:
    def test_save_output_csv(self, tmp_path) -> None:
        df = pd.DataFrame({"a": [1]})
        save_path = tmp_path / "test.csv"
        save_output(df, "test_data", str(save_path))
        assert os.path.exists(save_path)
        loaded_df = pd.read_csv(save_path)
        assert loaded_df["a"].iloc[0] == 1

    def test_save_output_json(self, tmp_path) -> None:
        data = {"key": "value"}
        save_path = tmp_path / "test.json"
        save_output(data, "test_data", str(save_path))
        assert os.path.exists(save_path)
        with open(save_path, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data["key"] == "value"

    def test_save_output_text(self, tmp_path) -> None:
        data = "hello world"
        save_path = tmp_path / "test.txt"
        save_output(data, "test_data", str(save_path))
        assert os.path.exists(save_path)
        with open(save_path, "r") as f:
            loaded_data = f.read()
        assert loaded_data == "hello world"

    def test_register_keys_from_json(self, tmp_path) -> None:
        keys = {"API_KEY": "12345"}
        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(keys, f)

        register_keys_from_json(str(config_path))
        assert os.environ["API_KEY"] == "12345"
