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

    symbol: papd.Series[papd.String] = pa.Field()
    date: papd.Series[papd.DateTime] = pa.Field()
    open: papd.Series[papd.Float] = pa.Field()
    high: papd.Series[papd.Float] = pa.Field()
    low: papd.Series[papd.Float] = pa.Field()
    close: papd.Series[papd.Float] = pa.Field()
    volume: papd.Series[papd.Int] = pa.Field()


class FinancialReportSchema(Schema):
    """Schema for generated financial reports."""

    company: papd.Series[papd.String] = pa.Field()
    report_type: papd.Series[papd.String] = pa.Field()
    content: papd.Series[papd.String] = pa.Field()
    timestamp: papd.Series[papd.DateTime] = pa.Field()


MarketData = papd.DataFrame[MarketDataSchema]
FinancialReports = papd.DataFrame[FinancialReportSchema]
