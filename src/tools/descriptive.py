import math
from typing import Any

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_complex_dtype,
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)

from .exceptions import (
    InvalidConfigurationError,
    InvalidDatasetError,
)
from .schemas import (
    CategoricalSummaryResult,
    CategoryFrequency,
    NumericSummaryResult,
)


def _validate_dataframe(dataframe: Any) -> None:
    if not isinstance(dataframe, pd.DataFrame):
        raise InvalidDatasetError("Expected a pandas DataFrame.")


def _normalize_statistic(value: Any) -> float | None:
    if pd.isna(value):
        return None

    numeric_value = float(value)

    if not math.isfinite(numeric_value):
        return None

    return numeric_value


def describe_numeric(
    dataframe: pd.DataFrame,
) -> list[NumericSummaryResult]:
    """Trả thống kê mô tả cho các cột numeric.

    Quy ước:
    - Boolean và complex không được coi là numeric cho descriptive summary.
    - Missing không được tính vào count.
    - Dùng pandas semantics cho mean/std/quantile.
    - NaN và infinite statistics được normalize thành None.
    - Duyệt cột theo position để hỗ trợ duplicate labels.
    - Function không mutate DataFrame.
    """

    _validate_dataframe(dataframe)

    results: list[NumericSummaryResult] = []

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        if (
            not is_numeric_dtype(series.dtype)
            or is_bool_dtype(series.dtype)
            or is_complex_dtype(series.dtype)
        ):
            continue

        count = int(series.notna().sum())
        missing_count = int(series.isna().sum())

        if count == 0:
            mean = None
            std = None
            min_value = None
            q1 = None
            median = None
            q3 = None
            max_value = None
        else:
            mean = _normalize_statistic(series.mean())
            std = _normalize_statistic(series.std())
            min_value = _normalize_statistic(series.min())
            q1 = _normalize_statistic(series.quantile(0.25))
            median = _normalize_statistic(series.quantile(0.50))
            q3 = _normalize_statistic(series.quantile(0.75))
            max_value = _normalize_statistic(series.max())

        results.append(
            NumericSummaryResult(
                position=position,
                column=str(column),
                dtype=str(series.dtype),
                count=count,
                missing_count=missing_count,
                mean=mean,
                std=std,
                min=min_value,
                q1=q1,
                median=median,
                q3=q3,
                max=max_value,
            )
        )

    return results


def describe_categorical(
    dataframe: pd.DataFrame,
    *,
    top_k: int = 5,
) -> list[CategoricalSummaryResult]:
    """Trả thống kê mô tả cho các cột categorical.

    Quy ước:
    - Object, string, category và boolean được coi là categorical.
    - Numeric, complex và datetime không thuộc categorical summary.
    - Missing không được tính trong unique_count hoặc top_values.
    - Rate của category dùng non-missing count làm denominator.
    - Chỉ trả tối đa top_k category phổ biến nhất.
    - Category được khai báo nhưng chưa xuất hiện không được report.
    - Duyệt theo position để hỗ trợ duplicate column labels.
    - Function không mutate DataFrame.
    """

    _validate_dataframe(dataframe)

    if (
        isinstance(top_k, bool)
        or not isinstance(top_k, int)
        or top_k <= 0
    ):
        raise InvalidConfigurationError(
            "top_k must be a positive integer."
        )

    results: list[CategoricalSummaryResult] = []

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        is_categorical = (
            is_bool_dtype(series.dtype)
            or is_object_dtype(series.dtype)
            or is_string_dtype(series.dtype)
            or isinstance(series.dtype, pd.CategoricalDtype)
        )

        if not is_categorical:
            continue

        count = int(series.notna().sum())
        missing_count = int(series.isna().sum())

        try:
            value_counts = series.value_counts(
                dropna=True,
                sort=True,
            )
        except TypeError as exc:
            raise InvalidDatasetError(
                f"Cannot calculate categorical frequencies for column "
                f"at position {position} because it contains "
                "values that cannot be counted."
            ) from exc

        # Categorical dtype có thể chứa category được khai báo
        # nhưng chưa xuất hiện trong dữ liệu.
        value_counts = value_counts[
            value_counts > 0
        ]

        unique_count = int(
            len(value_counts)
        )

        top_counts = value_counts.head(
            top_k
        )

        top_values: list[CategoryFrequency] = []

        for value, frequency in top_counts.items():
            frequency_count = int(
                frequency
            )

            rate = float(
                frequency_count / count
            )

            top_values.append(
                CategoryFrequency(
                    value=str(value),
                    count=frequency_count,
                    rate=rate,
                )
            )

        results.append(
            CategoricalSummaryResult(
                position=position,
                column=str(column),
                dtype=str(series.dtype),
                count=count,
                missing_count=missing_count,
                unique_count=unique_count,
                top_values=top_values,
            )
        )

    return results