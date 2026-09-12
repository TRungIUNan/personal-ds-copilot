"""
W01-T04 — Tool kiểm tra dataset

MỤC ĐÍCH
--------
Định nghĩa các tool nhỏ, chỉ đọc để lấy shape, schema, dtype, summary cột và
preview có giới hạn. Các tool này cung cấp evidence về DataFrame mà không đưa
ra business claim hoặc mutate input.

KIẾN THỨC CẦN HỌC
------------------
1. Khác nhau giữa metadata shape, schema và dtype của dữ liệu dạng bảng.
2. Vì sao preview phải có giới hạn và tường minh là có thể chuyển sang JSON.
3. Tên cột trùng, rỗng, bất thường và mixed-type ảnh hưởng tới contract thế nào.
4. Vì sao DataFrame rỗng cần quy ước có chủ đích thay vì giả định.

THỨ TỰ TRIỂN KHAI
------------------
1. Quyết định dạng return và schema model cho từng kết quả inspection.
2. Triển khai metadata shape và dtype trước.
3. Định nghĩa behavior cảnh báo tên cột cho tool schema/summary.
4. Cuối cùng triển khai preview có giới hạn, gồm cả normalize JSON.
5. Thêm test về tính bất biến, tính tất định và serialization.

RÀNG BUỘC QUAN TRỌNG
---------------------
- Không bao giờ sửa DataFrame input.
- Không expose toàn bộ dataset từ helper preview.
- Giữ output nhỏ, rõ ràng và có thể serialize đúng như contract đã hứa.
- Không suy luận target column, ID hoặc business meaning ở đây.
"""

from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from .exceptions import (
    InvalidConfigurationError,
    InvalidDatasetError,
)
from .schemas import (
    ColumnDtype,
    ColumnSummary,
    DtypeKind,
    DtypeResult,
    PreviewResult,
    SchemaResult,
    ShapeResult,
    ToolWarning,
)


def _validate_dataframe(dataframe: Any) -> None:
    """Đảm bảo input là pandas DataFrame."""

    if not isinstance(dataframe, pd.DataFrame):
        raise InvalidDatasetError(
            "Expected a pandas DataFrame."
        )


def _classify_dtype(dtype: Any) -> DtypeKind:
    """Chuẩn hóa pandas dtype thành nhóm dtype của inspection layer."""

    if is_bool_dtype(dtype):
        return "boolean"

    if is_datetime64_any_dtype(dtype):
        return "datetime"

    if is_numeric_dtype(dtype):
        return "numeric"

    if isinstance(dtype, pd.CategoricalDtype):
        return "categorical"

    if isinstance(dtype, pd.StringDtype):
        return "categorical"

    if is_object_dtype(dtype):
        return "categorical"

    return "unsupported"

def _to_json_safe(value: Any) -> Any:
    """Chuẩn hóa scalar pandas/numpy thành representation JSON-safe."""

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)
    
def get_shape(dataframe: pd.DataFrame) -> ShapeResult:
    """Trả về số dòng và số cột của một DataFrame."""
    _validate_dataframe(dataframe)

    rows, columns = dataframe.shape

    return ShapeResult(
        rows=rows,
        columns=columns,
    )

def get_schema(
    dataframe: pd.DataFrame,
) -> SchemaResult:
    """Trả về schema cột và các warning cấu trúc."""

    _validate_dataframe(dataframe)

    dtype_result = get_dtypes(dataframe)

    warnings: list[ToolWarning] = []

    duplicate_mask = dataframe.columns.duplicated(
        keep=False
    )

    for position, column in enumerate(dataframe.columns):

        if duplicate_mask[position]:
            warnings.append(
                ToolWarning(
                    code="DUPLICATE_COLUMN_NAME",
                    message="Column name is duplicated.",
                    context={
                        "position": position,
                        "column": str(column),
                    },
                )
            )

        if not isinstance(column, str):
            warnings.append(
                ToolWarning(
                    code="NON_STRING_COLUMN_NAME",
                    message="Column label is not a string.",
                    context={
                        "position": position,
                        "column": str(column),
                        "original_type": type(column).__name__,
                    },
                )
            )
            continue

        if column.strip() == "":
            warnings.append(
                ToolWarning(
                    code="EMPTY_COLUMN_NAME",
                    message="Column name is empty or whitespace-only.",
                    context={
                        "position": position,
                        "column": column,
                    },
                )
            )

        elif column != column.strip():
            warnings.append(
                ToolWarning(
                    code="COLUMN_NAME_WHITESPACE",
                    message="Column name contains leading or trailing whitespace.",
                    context={
                        "position": position,
                        "column": column,
                    },
                )
            )

    return SchemaResult(
        columns=dtype_result.columns,
        warnings=warnings,
    )

def get_dtypes(dataframe: pd.DataFrame) -> DtypeResult:
    """Trả về dtype gốc và dtype kind chuẩn hóa cho từng cột."""
    _validate_dataframe(dataframe)

    columns: list[ColumnDtype] = []

    for position, (column, dtype) in enumerate(
        zip(dataframe.columns, dataframe.dtypes)
    ):
        columns.append(
            ColumnDtype(
                position=position,
                column=str(column),
                dtype=str(dtype),
                dtype_kind=_classify_dtype(dtype),
            )
        )

    return DtypeResult(
        columns=columns,
    )


def get_column_summary(
    dataframe: pd.DataFrame,
) -> list[ColumnSummary]:
    """Trả về summary fact best-effort theo từng vị trí cột.

    Nếu pandas không thể đếm unique cho giá trị không hashable, ``unique`` là
    ``None``; các fact còn lại của cột vẫn được trả về.
    """

    _validate_dataframe(dataframe)

    summaries: list[ColumnSummary] = []

    total_rows = len(dataframe)

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        count = int(series.notna().sum())
        missing = int(series.isna().sum())

        if total_rows == 0:
            missing_rate = None
        else:
            missing_rate = float(missing / total_rows)

        try:
            unique = int(series.nunique(dropna=True))
        except TypeError:
            unique = None

        summaries.append(
            ColumnSummary(
                position=position,
                column=str(column),
                dtype=str(series.dtype),
                dtype_kind=_classify_dtype(series.dtype),
                count=count,
                missing=missing,
                missing_rate=missing_rate,
                unique=unique,
            )
        )

    return summaries


def preview_data(
    dataframe: pd.DataFrame,
    *,
    max_rows: int = 5,
    max_columns: int | None = 20,
) -> PreviewResult:
    """Trả về preview có giới hạn và JSON-safe."""

    _validate_dataframe(dataframe)

    if not isinstance(max_rows, int) or isinstance(max_rows, bool) or max_rows <= 0:
        raise InvalidConfigurationError(
            "max_rows must be a positive integer."
        )

    if max_columns is not None:
        if (
            not isinstance(max_columns, int)
            or isinstance(max_columns, bool)
            or max_columns <= 0
        ):
            raise InvalidConfigurationError(
                "max_columns must be None or a positive integer."
            )

    total_rows, total_columns = dataframe.shape

    returned_row_count = min(
        total_rows,
        max_rows,
    )

    if max_columns is None:
        returned_column_count = total_columns
    else:
        returned_column_count = min(
            total_columns,
            max_columns,
        )

    rows_truncated = total_rows > returned_row_count
    columns_truncated = total_columns > returned_column_count

    preview = dataframe.iloc[
        :returned_row_count,
        :returned_column_count,
    ]

    columns = [
        str(column)
        for column in preview.columns
    ]

    rows = [
        [
            _to_json_safe(value)
            for value in row
        ]
        for row in preview.itertuples(
            index=False,
            name=None,
        )
    ]
    return PreviewResult(
        columns=columns,
        rows=rows,
        total_rows=total_rows,
        total_columns=total_columns,
        returned_rows=returned_row_count,
        returned_columns=returned_column_count,
        rows_truncated=rows_truncated,
        columns_truncated=columns_truncated,
    )
