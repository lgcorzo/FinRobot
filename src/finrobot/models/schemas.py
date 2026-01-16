# %% IMPORTS

import typing as T

import pandas as pd
import pandera as pa
import pandera.typing as papd
import pandera.typing.common as padt

# %% TYPES

# Generic type for a dataframe container
TSchema = T.TypeVar("TSchema", bound="pa.DataFrameModel")

# %% SCHEMAS


class Schema(pa.DataFrameModel):
    """Base class for a dataframe schema.

    Use a schema to type your dataframe object.
    e.g., to communicate and validate its fields.
    """

    class Config:
        """Default configurations for all schemas.

        Parameters:
            coerce (bool): convert data type if possible.
            strict (bool): ensure the data type is correct.
        """

        coerce: bool = True
        strict: bool = True

    @classmethod
    def check(cls: T.Type[TSchema], data: pd.DataFrame) -> papd.DataFrame[TSchema]:
        """Check the dataframe with this schema.

        Args:
            data (pd.DataFrame): dataframe to check.

        Returns:
            papd.DataFrame[TSchema]: validated dataframe.
        """
        return T.cast(papd.DataFrame[TSchema], cls.validate(data))


class MetadataSchema(Schema):
    """Schema for metadata in outputs."""

    timestamp: papd.Series[str] = pa.Field()
    model_version: papd.Series[str] = pa.Field()


class InputsSchema(Schema):
    """Schema for validating large string inputs."""

    input: papd.Series[str] = pa.Field()


class OutputsSchema(Schema):
    """Schema for structured JSON outputs."""

    response: papd.Series[str] = pa.Field()
    metadata: papd.Series[object] = pa.Field()


class TargetsSchema(Schema):
    """Schema for the project target."""

    input_target: papd.Series[str] = pa.Field()
    response: papd.Series[str] = pa.Field()


class SHAPValuesSchema(Schema):
    """Schema for SHAP values."""

    sample: papd.Series[str] = pa.Field()
    explanation: papd.Series[str] = pa.Field()
    shap_value: papd.Series[float] = pa.Field()

    class Config:
        strict: bool = False


class FeatureImportancesSchema(Schema):
    """Schema for feature importances."""

    feature: papd.Series[str] = pa.Field()
    importance: papd.Series[float] = pa.Field()


Inputs = papd.DataFrame[InputsSchema]
Targets = papd.DataFrame[TargetsSchema]
Outputs = papd.DataFrame[OutputsSchema]
SHAPValues = papd.DataFrame[SHAPValuesSchema]
FeatureImportances = papd.DataFrame[FeatureImportancesSchema]
