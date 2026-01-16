import pandas as pd
import pytest
from finrobot.models.schemas import InputsSchema, MetadataSchema, OutputsSchema


def test_inputs_schema_valid() -> None:
    df = pd.DataFrame({"input": ["text 1", "text 2"]})
    validated = InputsSchema.validate(df)
    assert not validated.empty
    assert list(validated.columns) == ["input"]


def test_inputs_schema_invalid() -> None:
    df = pd.DataFrame({"wrong_column": ["text 1"]})
    with pytest.raises(Exception):  # Pandera SchemaError
        InputsSchema.validate(df)


def test_metadata_schema() -> None:
    df = pd.DataFrame({"timestamp": ["2025-01-15T12:00:00Z"], "model_version": ["v1.0.0"]})
    validated = MetadataSchema.validate(df)
    assert not validated.empty


def test_outputs_schema() -> None:
    df = pd.DataFrame({"response": ["some response"], "metadata": [{"timestamp": "...", "model_version": "..."}]})
    validated = OutputsSchema.validate(df)
    assert not validated.empty
    assert "response" in validated.columns
    assert "metadata" in validated.columns
