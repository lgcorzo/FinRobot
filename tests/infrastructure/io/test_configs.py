"""Tests for IO configs module."""

import os
import tempfile

from finrobot.infrastructure.io.configs import (
    merge_configs,
    parse_file,
    parse_string,
    to_object,
)


class TestConfigs:
    """Test suite for OmegaConf configuration utilities."""

    def test_parse_string_yaml(self) -> None:
        """Test parsing a YAML string."""
        yaml_str = "key: value\nnumber: 42"
        result = parse_string(yaml_str)

        assert result.key == "value"
        assert result.number == 42

    def test_parse_string_nested(self) -> None:
        """Test parsing nested YAML structure."""
        yaml_str = """
        parent:
            child: value
            list:
                - item1
                - item2
        """
        result = parse_string(yaml_str)

        assert result.parent.child == "value"
        assert len(result.parent.list) == 2

    def test_parse_file(self) -> None:
        """Test parsing a YAML file."""
        yaml_content = "name: test\nversion: 1.0"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            result = parse_file(temp_path)
            assert result.name == "test"
            assert result.version == 1.0
        finally:
            os.unlink(temp_path)

    def test_merge_configs(self) -> None:
        """Test merging multiple configurations."""
        config1 = parse_string("a: 1\nb: 2")
        config2 = parse_string("b: 3\nc: 4")

        # merge_configs takes a sequence (list) of configs
        merged = merge_configs([config1, config2])

        assert merged.a == 1
        assert merged.b == 3  # Overwritten by config2
        assert merged.c == 4

    def test_to_object(self) -> None:
        """Test converting OmegaConf to Python object."""
        config = parse_string("key: value\nnumber: 42")
        obj = to_object(config)

        assert isinstance(obj, dict)
        assert obj["key"] == "value"
        assert obj["number"] == 42
