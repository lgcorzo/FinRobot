"""Schemas for FinRobot data validation."""

import typing as T

import pandas as pd
import pandera as pa
import pandera.typing as papd

# %% TYPES

TSchema = T.TypeVar("TSchema", bound="pa.DataFrameModel")

# %% SCHEMAS


class Schema(pa.DataFrameModel):
    """Base class for a dataframe schema."""

    class Config:
        coerce: bool = True
        strict: bool = True

    @classmethod
    def check(cls: T.Type[TSchema], data: pd.DataFrame) -> papd.DataFrame[TSchema]:
        return T.cast(papd.DataFrame[TSchema], cls.validate(data))


class MarketDataSchema(Schema):
    """Schema for market data."""

    symbol: papd.Series[str] = pa.Field()
    date: papd.Series[T.Any] = pa.Field()
    open: papd.Series[float] = pa.Field()
    high: papd.Series[float] = pa.Field()
    low: papd.Series[float] = pa.Field()
    close: papd.Series[float] = pa.Field()
    volume: papd.Series[int] = pa.Field()


class FinancialReportSchema(Schema):
    """Schema for generated financial reports."""

    company: papd.Series[str] = pa.Field()
    report_type: papd.Series[str] = pa.Field()
    content: papd.Series[str] = pa.Field()
    timestamp: papd.Series[T.Any] = pa.Field()


MarketData = papd.DataFrame[MarketDataSchema]
FinancialReports = papd.DataFrame[FinancialReportSchema]
