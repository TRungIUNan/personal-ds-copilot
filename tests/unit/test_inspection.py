"""
W01-T04 — Kiểm thử behavior của inspection

Test bao phủ đường đi chuẩn, trường hợp biên, input không hợp lệ, tính bất biến,
JSON serialization và tính tất định.
"""

import json
from typing import Any, cast

import numpy as np
import pandas as pd
import pytest

from src.tools.exceptions import (
    InvalidConfigurationError,
    InvalidDatasetError,
)
from src.tools.inspection import (
    get_column_summary,
    get_dtypes,
    get_schema,
    get_shape,
    preview_data,
)


def _assert_result_is_json_serializable(result) -> None:
    """Kiểm tra result Pydantic có thể chuyển sang JSON."""

    payload = result.model_dump_json()

    assert isinstance(payload, str)
    json.loads(payload)


def _warnings_with_code(result, code: str):
    """Lấy các warning có cùng code để assertion theo behavior rõ ràng."""

    return [warning for warning in result.warnings if warning.code == code]


def _warning_context(warning) -> dict[str, Any]:
    """Trả về context sau khi xác nhận warning có context."""

    assert warning.context is not None
    return warning.context


def test_get_shape_returns_row_and_column_counts() -> None:
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        }
    )

    result = get_shape(df)

    assert result.rows == 3
    assert result.columns == 2

def test_get_shape_handles_empty_dataframe() -> None:
    df = pd.DataFrame()

    result = get_shape(df)

    assert result.rows == 0
    assert result.columns == 0

def test_get_shape_handles_zero_rows_with_columns(empty_dataframe) -> None:
    result = get_shape(empty_dataframe)

    assert result.rows == 0
    assert result.columns == 4

def test_get_shape_does_not_modify_dataframe() -> None:
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
        }
    )

    before = df.copy(deep=True)

    get_shape(df)

    pd.testing.assert_frame_equal(df, before)

def test_get_shape_result_is_json_serializable() -> None:
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
        }
    )

    result = get_shape(df)

    _assert_result_is_json_serializable(result)


def test_get_dtypes_returns_expected_dtype_information() -> None:
    """get_dtypes trả đúng raw dtype, vị trí và dtype_kind cho nhiều dtype."""

    df = pd.DataFrame(
        {
            "age": pd.Series([21, 32], dtype="int64"),
            "salary": pd.Series([100.0, 200.0], dtype="float64"),
            "city": pd.Series(["Hanoi", "Danang"], dtype="object"),
            "active": pd.Series([True, False], dtype="bool"),
            "created_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        }
    )

    result = get_dtypes(df)

    assert len(result.columns) == 5
    assert [item.position for item in result.columns] == [0, 1, 2, 3, 4]
    assert [item.column for item in result.columns] == [
        "age",
        "salary",
        "city",
        "active",
        "created_at",
    ]
    assert [item.dtype_kind for item in result.columns] == [
        "numeric",
        "numeric",
        "categorical",
        "boolean",
        "datetime",
    ]
    assert result.columns[0].dtype == "int64"
    assert result.columns[3].dtype == "bool"
    assert result.columns[4].dtype.startswith("datetime64[")
    assert result.columns[4].dtype_kind == "datetime"


def test_get_dtypes_handles_empty_dataframe() -> None:
    """DataFrame hoàn toàn rỗng cho result có danh sách cột rỗng."""

    result = get_dtypes(pd.DataFrame())

    assert result.columns == []


def test_get_dtypes_handles_zero_rows_with_declared_dtypes(empty_dataframe) -> None:
    """get_dtypes dùng declared dtype ngay cả khi DataFrame không có row."""

    result = get_dtypes(empty_dataframe)

    assert len(result.columns) == 4
    assert result.columns[0].column == "customer_id"
    assert result.columns[0].dtype == "int64"
    assert result.columns[0].dtype_kind == "numeric"
    assert result.columns[1].column == "age"
    assert result.columns[1].dtype == "float64"
    assert result.columns[1].dtype_kind == "numeric"
    assert result.columns[2].column == "city"
    assert result.columns[2].dtype == "string"
    assert result.columns[2].dtype_kind == "categorical"
    assert result.columns[3].column == "active"
    assert result.columns[3].dtype == "boolean"
    assert result.columns[3].dtype_kind == "boolean"


def test_get_dtypes_classifies_string_dtype_as_categorical() -> None:
    """Pandas StringDtype được phân loại là categorical."""

    df = pd.DataFrame({"name": pd.Series(["A", "B"], dtype="string")})

    result = get_dtypes(df)

    assert result.columns[0].dtype == "string"
    assert result.columns[0].dtype_kind == "categorical"


def test_get_dtypes_classifies_category_dtype_as_categorical() -> None:
    """Pandas CategoricalDtype được phân loại là categorical."""

    df = pd.DataFrame(
        {
            "priority": pd.Series(
                ["low", "medium", "high"],
                dtype="category",
            )
        }
    )

    result = get_dtypes(df)

    assert result.columns[0].dtype == "category"
    assert result.columns[0].dtype_kind == "categorical"


def test_get_dtypes_handles_nullable_dtypes() -> None:
    """Nullable Int64 là numeric và nullable boolean là boolean."""

    df = pd.DataFrame(
        {
            "nullable_int": pd.Series([1, None, 3], dtype="Int64"),
            "nullable_bool": pd.Series([True, None, False], dtype="boolean"),
        }
    )

    result = get_dtypes(df)

    assert result.columns[0].dtype == "Int64"
    assert result.columns[0].dtype_kind == "numeric"
    assert result.columns[1].dtype == "boolean"
    assert result.columns[1].dtype_kind == "boolean"


def test_get_dtypes_classifies_mixed_object_as_categorical(
    mixed_dtype_dataframe,
) -> None:
    """Object mixed value giữ raw dtype object và được phân loại categorical."""

    result = get_dtypes(mixed_dtype_dataframe)

    assert [item.column for item in result.columns] == [
        "score",
        "city",
        "event_time",
        "active",
        "mixed_value",
    ]
    assert [item.dtype_kind for item in result.columns] == [
        "numeric",
        "categorical",
        "datetime",
        "boolean",
        "categorical",
    ]
    assert result.columns[-1].dtype == "object"
    assert result.columns[-1].dtype_kind == "categorical"


def test_get_dtypes_marks_unhandled_dtype_as_unsupported() -> None:
    """Timedelta dtype chưa được hỗ trợ được đánh dấu unsupported."""

    df = pd.DataFrame(
        {
            "duration": pd.to_timedelta(["1 days", "2 days"]),
        }
    )

    result = get_dtypes(df)

    assert result.columns[0].dtype.startswith("timedelta64[")
    assert result.columns[0].dtype_kind == "unsupported"


def test_get_dtypes_preserves_duplicate_columns_by_position() -> None:
    """Tên cột trùng vẫn tạo đủ result theo vị trí zero-based."""

    df = pd.DataFrame(
        [
            [1, "A"],
            [2, "B"],
        ],
        columns=["value", "value"],
    )

    result = get_dtypes(df)

    assert len(result.columns) == 2
    assert result.columns[0].position == 0
    assert result.columns[1].position == 1
    assert result.columns[0].column == "value"
    assert result.columns[1].column == "value"


def test_get_dtypes_serializes_non_string_column_label() -> None:
    """Column label không phải string được serialize bằng str()."""

    df = pd.DataFrame({100: [1, 2, 3]})

    result = get_dtypes(df)

    assert result.columns[0].column == "100"


def test_get_dtypes_preserves_column_order() -> None:
    """Output giữ nguyên thứ tự cột nguồn và không tự sort."""

    df = pd.DataFrame(
        {
            "z": [1, 2],
            "a": ["A", "B"],
            "m": [True, False],
        }
    )

    result = get_dtypes(df)

    assert [item.position for item in result.columns] == [0, 1, 2]
    assert [item.column for item in result.columns] == ["z", "a", "m"]


def test_get_dtypes_does_not_modify_dataframe() -> None:
    """get_dtypes không thay đổi DataFrame nguồn."""

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        }
    )
    before = df.copy(deep=True)

    get_dtypes(df)

    pd.testing.assert_frame_equal(df, before)


def test_get_dtypes_is_deterministic() -> None:
    """Cùng input cho cùng DtypeResult qua hai lần gọi."""

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        }
    )

    first = get_dtypes(df)
    second = get_dtypes(df)

    assert first == second


def test_get_dtypes_result_is_json_serializable() -> None:
    """DtypeResult có thể chuyển sang JSON và parse lại được."""

    df = pd.DataFrame(
        {
            "id": [1, 2],
            "active": [True, False],
        }
    )

    result = get_dtypes(df)

    _assert_result_is_json_serializable(result)


# ============================================================
# get_schema
# ============================================================


def test_get_schema_returns_columns_without_warnings_for_clean_dataframe() -> None:
    """Schema sạch giữ metadata cột đúng và không phát warning."""

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
            "value": [10.0, 20.0, 30.0],
        }
    )

    result = get_schema(df)

    assert len(result.columns) == 3
    assert [item.position for item in result.columns] == [0, 1, 2]
    assert [item.column for item in result.columns] == ["id", "name", "value"]
    assert [item.dtype_kind for item in result.columns] == [
        "numeric",
        "categorical",
        "numeric",
    ]
    assert result.warnings == []


def test_get_schema_handles_empty_dataframe() -> None:
    """Schema của DataFrame rỗng có columns và warnings đều rỗng."""

    result = get_schema(pd.DataFrame())

    assert result.columns == []
    assert result.warnings == []


def test_get_schema_handles_zero_rows_with_declared_columns() -> None:
    """Schema vẫn giữ dtype của cột được khai báo khi không có row."""

    df = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "name": pd.Series(dtype="string"),
        }
    )

    result = get_schema(df)

    assert len(result.columns) == 2
    assert [item.column for item in result.columns] == ["id", "name"]
    assert [item.dtype_kind for item in result.columns] == [
        "numeric",
        "categorical",
    ]
    assert result.warnings == []


def test_get_schema_warns_for_duplicate_column_names() -> None:
    """Schema cảnh báo mọi vị trí có tên cột duplicate mà không mất cột."""

    df = pd.DataFrame(
        [
            [1, "A", 100],
            [2, "B", 200],
        ],
        columns=["id", "name", "id"],
    )

    result = get_schema(df)
    duplicate_warnings = _warnings_with_code(result, "DUPLICATE_COLUMN_NAME")

    assert len(result.columns) == 3
    assert [item.position for item in result.columns] == [0, 1, 2]
    assert [item.column for item in result.columns] == ["id", "name", "id"]
    assert len(duplicate_warnings) == 2
    assert [_warning_context(warning)["position"] for warning in duplicate_warnings] == [0, 2]


def test_get_schema_warns_for_empty_column_name() -> None:
    """Tên cột rỗng tạo EMPTY_COLUMN_NAME với position đúng."""

    df = pd.DataFrame(
        [[1, "", "A"], [2, "", "B"]],
        columns=["id", "", "name"],
    )

    result = get_schema(df)
    empty_warnings = _warnings_with_code(result, "EMPTY_COLUMN_NAME")

    assert len(empty_warnings) == 1
    assert _warning_context(empty_warnings[0])["position"] == 1


def test_get_schema_treats_whitespace_only_column_as_empty() -> None:
    """Tên cột chỉ có whitespace là empty, không đồng thời là whitespace warning."""

    df = pd.DataFrame(
        [[1, "A", "X"], [2, "B", "Y"]],
        columns=["id", "   ", "name"],
    )

    result = get_schema(df)

    assert len(_warnings_with_code(result, "EMPTY_COLUMN_NAME")) == 1
    assert len(_warnings_with_code(result, "COLUMN_NAME_WHITESPACE")) == 0
    assert _warning_context(result.warnings[0])["position"] == 1


def test_get_schema_warns_for_leading_or_trailing_whitespace() -> None:
    """Tên cột có whitespace ở đầu/cuối được cảnh báo nhưng không bị trim."""

    df = pd.DataFrame(
        [[1, "A", 10], [2, "B", 20]],
        columns=["id", " name ", "value"],
    )

    result = get_schema(df)
    whitespace_warnings = _warnings_with_code(result, "COLUMN_NAME_WHITESPACE")

    assert len(whitespace_warnings) == 1
    assert _warning_context(whitespace_warnings[0])["position"] == 1
    assert _warning_context(whitespace_warnings[0])["column"] == " name "
    assert result.columns[1].column == " name "


def test_get_schema_warns_for_non_string_column_label() -> None:
    """Label không phải string tạo warning nhưng vẫn giữ column dưới dạng string."""

    df = pd.DataFrame(
        {
            123: [1, 2],
            "name": ["A", "B"],
        }
    )

    result = get_schema(df)
    non_string_warnings = _warnings_with_code(result, "NON_STRING_COLUMN_NAME")

    assert len(non_string_warnings) == 1
    assert _warning_context(non_string_warnings[0])["position"] == 0
    assert _warning_context(non_string_warnings[0])["column"] == "123"
    assert _warning_context(non_string_warnings[0])["original_type"] == "int"
    assert result.columns[0].column == "123"


def test_get_schema_reports_multiple_column_name_warnings() -> None:
    """Một DataFrame có thể tạo nhiều loại warning tên cột có cấu trúc."""

    df = pd.DataFrame(
        [
            [1, "A", 2, "", 123],
            [2, "B", 3, "", 456],
        ],
        columns=["id", " name ", "id", "", 123],
    )

    result = get_schema(df)
    codes = {warning.code for warning in result.warnings}

    assert {
        "DUPLICATE_COLUMN_NAME",
        "COLUMN_NAME_WHITESPACE",
        "EMPTY_COLUMN_NAME",
        "NON_STRING_COLUMN_NAME",
    }.issubset(codes)

    duplicate_positions = [
        _warning_context(warning)["position"]
        for warning in _warnings_with_code(result, "DUPLICATE_COLUMN_NAME")
    ]
    assert duplicate_positions == [0, 2]


def test_get_schema_preserves_column_order() -> None:
    """Schema giữ nguyên thứ tự cột nguồn và không tự sort."""

    df = pd.DataFrame(
        {
            "z": [1, 2],
            "a": ["A", "B"],
            "m": [True, False],
        }
    )

    result = get_schema(df)

    assert [item.column for item in result.columns] == ["z", "a", "m"]
    assert [item.position for item in result.columns] == [0, 1, 2]


def test_get_schema_preserves_duplicate_column_dtype_metadata() -> None:
    """Duplicate label vẫn giữ đủ dtype metadata theo từng position."""

    df = pd.DataFrame(
        [
            [1, "A"],
            [2, "B"],
        ],
        columns=["value", "value"],
    )

    result = get_schema(df)

    assert len(result.columns) == 2
    assert [item.position for item in result.columns] == [0, 1]
    assert [item.column for item in result.columns] == ["value", "value"]


def test_get_schema_rejects_non_dataframe_input() -> None:
    """get_schema từ chối input không phải pandas DataFrame."""

    invalid_dataframe = cast(Any, [1, 2, 3])

    with pytest.raises(InvalidDatasetError):
        get_schema(invalid_dataframe)


def test_get_schema_does_not_modify_dataframe() -> None:
    """get_schema không trim, rename hoặc deduplicate DataFrame nguồn."""

    df = pd.DataFrame(
        [[1, "A", 2], [2, "B", 3]],
        columns=["id", " name ", "id"],
    )
    before = df.copy(deep=True)
    before_columns = list(df.columns)

    get_schema(df)

    pd.testing.assert_frame_equal(df, before)
    assert list(df.columns) == before_columns


def test_get_schema_is_deterministic() -> None:
    """Cùng input cho cùng columns, warnings và context qua hai lần gọi."""

    df = pd.DataFrame(
        [[1, "A", 2], [2, "B", 3]],
        columns=["id", " name ", "id"],
    )

    first = get_schema(df)
    second = get_schema(df)

    assert first == second


def test_get_schema_result_is_json_serializable() -> None:
    """SchemaResult có warning vẫn chuyển sang JSON và parse lại được."""

    df = pd.DataFrame(
        [[1, "A"], [2, "B"]],
        columns=["id", " name "],
    )

    result = get_schema(df)

    _assert_result_is_json_serializable(result)


# ============================================================
# get_column_summary
# ============================================================


def test_get_column_summary_returns_expected_facts() -> None:
    """Summary trả đúng fact cấu trúc cho các cột numeric/categorical/boolean."""

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "age": [20.0, None, 30.0, 40.0],
            "city": ["HN", "HN", None, "HCM"],
            "active": [True, False, True, True],
        }
    )

    result = get_column_summary(df)

    assert len(result) == 4

    assert result[0].position == 0
    assert result[0].column == "id"
    assert result[0].dtype_kind == "numeric"
    assert result[0].dtype == "int64"
    assert result[0].count == 4
    assert result[0].missing == 0
    assert result[0].missing_rate == 0.0
    assert result[0].unique == 4

    assert result[1].position == 1
    assert result[1].column == "age"
    assert result[1].count == 3
    assert result[1].missing == 1
    assert result[1].missing_rate == pytest.approx(0.25)
    assert result[1].unique == 3

    assert result[2].position == 2
    assert result[2].column == "city"
    assert result[2].dtype_kind == "categorical"
    assert result[2].count == 3
    assert result[2].missing == 1
    assert result[2].missing_rate == pytest.approx(0.25)
    assert result[2].unique == 2

    assert result[3].position == 3
    assert result[3].column == "active"
    assert result[3].dtype == "bool"
    assert result[3].dtype_kind == "boolean"
    assert result[3].count == 4
    assert result[3].missing == 0
    assert result[3].missing_rate == 0.0
    assert result[3].unique == 2


def test_get_column_summary_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả về danh sách summary rỗng."""

    result = get_column_summary(pd.DataFrame())

    assert result == []


def test_get_column_summary_handles_zero_rows_with_declared_columns() -> None:
    """Summary giữ declared dtype khi DataFrame có cột nhưng không có row."""

    df = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "name": pd.Series(dtype="string"),
        }
    )

    result = get_column_summary(df)

    assert len(result) == 2
    assert result[0].column == "id"
    assert result[0].dtype_kind == "numeric"
    assert result[0].count == 0
    assert result[0].missing == 0
    assert result[0].missing_rate is None
    assert result[0].unique == 0
    assert result[1].column == "name"
    assert result[1].dtype_kind == "categorical"
    assert result[1].count == 0
    assert result[1].missing == 0
    assert result[1].missing_rate is None
    assert result[1].unique == 0


def test_get_column_summary_handles_all_null_column() -> None:
    """Cột all-null không gây crash và có unique bằng 0."""

    df = pd.DataFrame({"value": [None, None, None]})

    result = get_column_summary(df)

    assert result[0].count == 0
    assert result[0].missing == 3
    assert result[0].missing_rate == 1.0
    assert result[0].unique == 0


def test_get_column_summary_excludes_missing_from_unique_count() -> None:
    """Unique count không tính missing value là một unique value."""

    df = pd.DataFrame({"city": ["HN", "HN", "HCM", None]})

    result = get_column_summary(df)

    assert result[0].unique == 2
    assert result[0].missing == 1
    assert result[0].missing_rate == pytest.approx(0.25)


def test_get_column_summary_preserves_duplicate_columns_by_position() -> None:
    """Duplicate column vẫn có summary riêng theo vị trí nguồn."""

    df = pd.DataFrame(
        [
            [1, "A"],
            [2, "B"],
        ],
        columns=["value", "value"],
    )

    result = get_column_summary(df)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[1].position == 1
    assert result[0].column == "value"
    assert result[1].column == "value"
    assert result[0].dtype_kind == "numeric"
    assert result[1].dtype_kind == "categorical"
    assert result[0].unique == 2
    assert result[1].unique == 2


def test_get_column_summary_serializes_non_string_column_label() -> None:
    """Column label không phải string được biểu diễn bằng str(column)."""

    df = pd.DataFrame({123: [1, 2, 3]})

    result = get_column_summary(df)

    assert result[0].column == "123"


def test_get_column_summary_handles_datetime_column() -> None:
    """Datetime column có dtype kind và missing rate đúng."""

    parsed_dates = pd.to_datetime(
        [
        "2026-01-01",
        "2026-01-03",
        ]
    )

    df = pd.DataFrame(
        {
            "created_at": [
                parsed_dates[0],
                pd.NaT,
                parsed_dates[1],
            ]
        }
    )

    result = get_column_summary(df)

    assert result[0].dtype_kind == "datetime"
    assert result[0].dtype.startswith("datetime64[")
    assert result[0].count == 2
    assert result[0].missing == 1
    assert result[0].missing_rate == pytest.approx(1 / 3)
    assert result[0].unique == 2


def test_get_column_summary_handles_boolean_column() -> None:
    """Nullable boolean column được summary đúng theo missing convention."""

    df = pd.DataFrame(
        {
            "active": pd.Series([True, None, False], dtype="boolean"),
        }
    )

    result = get_column_summary(df)

    assert result[0].dtype_kind == "boolean"
    assert result[0].count == 2
    assert result[0].missing == 1
    assert result[0].missing_rate == pytest.approx(1 / 3)
    assert result[0].unique == 2


def test_get_column_summary_handles_mixed_object_column() -> None:
    """Object mixed value giữ raw dtype object và không suy luận sâu hơn."""

    df = pd.DataFrame(
        {
            "mixed": pd.Series([1, "A", 3.5], dtype="object"),
        }
    )

    result = get_column_summary(df)

    assert result[0].dtype == "object"
    assert result[0].dtype_kind == "categorical"
    assert result[0].count == 3
    assert result[0].missing == 0
    assert result[0].unique == 3


def test_get_column_summary_handles_unhashable_values_for_active_pandas_runtime() -> None:
    """Summary phản ánh đúng capability nunique của pandas đang chạy."""

    df = pd.DataFrame(
        {
            "items": [[1, 2], [3, 4], [1, 2]],
        }
    )

    try:
        expected_unique = int(df["items"].nunique(dropna=True))
    except TypeError:
        expected_unique = None

    result = get_column_summary(df)

    assert result[0].count == 3
    assert result[0].missing == 0
    assert result[0].unique == expected_unique


def test_get_column_summary_preserves_column_order() -> None:
    """Summary giữ nguyên thứ tự cột nguồn và không tự sort."""

    df = pd.DataFrame(
        {
            "z": [1, 2],
            "a": ["A", "B"],
            "m": [True, False],
        }
    )

    result = get_column_summary(df)

    assert [summary.column for summary in result] == ["z", "a", "m"]
    assert [summary.position for summary in result] == [0, 1, 2]


def test_get_column_summary_rejects_non_dataframe_input() -> None:
    """get_column_summary từ chối input không phải pandas DataFrame."""

    invalid_dataframe = cast(Any, [1, 2, 3])

    with pytest.raises(InvalidDatasetError):
        get_column_summary(invalid_dataframe)


def test_get_column_summary_does_not_modify_dataframe() -> None:
    """Summary không fill, đổi dtype, rename hoặc sort DataFrame nguồn."""

    df = pd.DataFrame(
        [[1, "A", 2], [2, "B", 3]],
        columns=["id", " name ", "id"],
    )
    before = df.copy(deep=True)
    before_columns = list(df.columns)

    get_column_summary(df)

    pd.testing.assert_frame_equal(df, before)
    assert list(df.columns) == before_columns


def test_get_column_summary_is_deterministic() -> None:
    """Cùng input cho cùng summary qua hai lần gọi."""

    df = pd.DataFrame(
        [[1, "A", None], [2, "B", 3]],
        columns=["id", "name", "value"],
    )

    first = get_column_summary(df)
    second = get_column_summary(df)

    assert first == second


def test_get_column_summary_is_json_serializable() -> None:
    """Danh sách ColumnSummary có thể chuyển sang JSON."""

    df = pd.DataFrame(
        [[1, "A"], [2, None]],
        columns=["id", "name"],
    )

    result = get_column_summary(df)
    payload = [item.model_dump() for item in result]

    json.dumps(payload)


def test_get_column_summary_uses_numeric_rate_convention() -> None:
    """Missing rate được biểu diễn bằng số trong khoảng 0.0 đến 1.0."""

    df = pd.DataFrame({"value": [1, None, 3, 4]})

    result = get_column_summary(df)

    missing_rate = result[0].missing_rate
    assert missing_rate is not None
    assert missing_rate == pytest.approx(0.25)
    assert 0.0 <= missing_rate <= 1.0


# ============================================================
# preview_data
# ============================================================


def test_preview_data_returns_expected_preview_and_metadata() -> None:
    """Preview giữ đúng thứ tự dữ liệu và trả về metadata giới hạn."""

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": ["A", "B", "C", "D"],
            "value": [10, 20, 30, 40],
        }
    )

    result = preview_data(df, max_rows=2, max_columns=2)

    assert result.columns == ["id", "name"]
    assert result.rows == [[1, "A"], [2, "B"]]
    assert result.total_rows == 4
    assert result.total_columns == 3
    assert result.returned_rows == 2
    assert result.returned_columns == 2
    assert result.rows_truncated is True
    assert result.columns_truncated is True


def test_preview_data_uses_default_limits() -> None:
    """Giới hạn mặc định là 5 dòng và 20 cột."""

    df = pd.DataFrame(
        [[row * 25 + column for column in range(25)] for row in range(10)],
        columns=[f"column_{index}" for index in range(25)],
    )

    result = preview_data(df)

    assert result.returned_rows == 5
    assert result.returned_columns == 20
    assert result.rows_truncated is True
    assert result.columns_truncated is True


def test_preview_data_respects_row_limit() -> None:
    """Giới hạn dòng không làm mất toàn bộ các cột."""

    df = pd.DataFrame({"id": [1, 2, 3, 4], "name": ["A", "B", "C", "D"]})

    result = preview_data(df, max_rows=3, max_columns=20)

    assert result.returned_rows == 3
    assert result.returned_columns == 2
    assert result.rows_truncated is True
    assert result.columns_truncated is False


def test_preview_data_respects_column_limit() -> None:
    """Giới hạn cột không làm mất các dòng còn trong giới hạn."""

    df = pd.DataFrame(
        {
            "a": [1, 2],
            "b": [3, 4],
            "c": [5, 6],
        }
    )

    result = preview_data(df, max_rows=5, max_columns=2)

    assert result.returned_rows == 2
    assert result.returned_columns == 2
    assert result.rows_truncated is False
    assert result.columns_truncated is True


def test_preview_data_reports_no_truncation_when_within_limits() -> None:
    """Preview nhỏ hơn giới hạn không bị đánh dấu cắt ngắn."""

    df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})

    result = preview_data(df, max_rows=5, max_columns=20)

    assert result.returned_rows == result.total_rows == 2
    assert result.returned_columns == result.total_columns == 2
    assert result.rows_truncated is False
    assert result.columns_truncated is False


def test_preview_data_allows_all_columns_when_max_columns_is_none() -> None:
    """max_columns=None cho phép trả về toàn bộ cột nhưng vẫn giới hạn dòng."""

    df = pd.DataFrame(
        [[row * 25 + column for column in range(25)] for row in range(4)],
        columns=[f"column_{index}" for index in range(25)],
    )

    result = preview_data(df, max_rows=2, max_columns=None)

    assert result.returned_rows == 2
    assert result.returned_columns == result.total_columns == 25
    assert result.rows_truncated is True
    assert result.columns_truncated is False
    assert len(result.rows[0]) == 25


def test_preview_data_handles_empty_dataframe() -> None:
    """DataFrame 0x0 tạo preview rỗng mà không phát sinh lỗi."""

    result = preview_data(pd.DataFrame())

    assert result.columns == []
    assert result.rows == []
    assert result.total_rows == 0
    assert result.total_columns == 0
    assert result.returned_rows == 0
    assert result.returned_columns == 0
    assert result.rows_truncated is False
    assert result.columns_truncated is False


def test_preview_data_handles_zero_rows_with_columns() -> None:
    """DataFrame không có dòng vẫn giữ nguyên các cột đã khai báo."""

    df = pd.DataFrame(columns=["id", "name", "value"])

    result = preview_data(df)

    assert result.columns == ["id", "name", "value"]
    assert result.rows == []
    assert result.total_rows == 0
    assert result.total_columns == 3
    assert result.returned_rows == 0
    assert result.returned_columns == 3
    assert result.rows_truncated is False
    assert result.columns_truncated is False


def test_preview_data_preserves_duplicate_column_names() -> None:
    """Tên cột trùng vẫn được giữ đủ theo vị trí."""

    df = pd.DataFrame(
        [[1, 100, 200], [2, 300, 400]],
        columns=["id", "value", "value"],
    )

    result = preview_data(df)

    assert result.columns == ["id", "value", "value"]
    assert result.rows == [[1, 100, 200], [2, 300, 400]]


def test_preview_data_serializes_non_string_column_labels() -> None:
    """Nhãn cột không phải chuỗi được chuyển thành chuỗi mà không cảnh báo."""

    df = pd.DataFrame({123: [1, 2], "name": ["A", "B"]})

    result = preview_data(df)

    assert result.columns == ["123", "name"]


def test_preview_data_normalizes_missing_values_to_none() -> None:
    """Các dạng giá trị thiếu đều trở thành Python None."""

    df = pd.DataFrame(
        {
            "none": pd.Series([None], dtype="object"),
            "nan": pd.Series([np.nan], dtype="object"),
            "pd_na": pd.Series([pd.NA], dtype="object"),
            "nat": pd.Series([pd.NaT], dtype="object"),
        }
    )

    result = preview_data(df)

    assert result.rows == [[None, None, None, None]]


def test_preview_data_serializes_timestamp_as_iso_string() -> None:
    """Timestamp được chuyển thành chuỗi ISO trong preview."""

    df = pd.DataFrame({"created_at": [pd.Timestamp("2026-09-08")]})

    result = preview_data(df)

    value = result.rows[0][0]
    assert isinstance(value, str)
    assert value.startswith("2026-09-08")


def test_preview_data_converts_numpy_scalars_to_python_scalars() -> None:
    """Numpy scalar được chuyển thành kiểu primitive tương ứng của Python."""

    df = pd.DataFrame(
        {
            "integer": [np.int64(10)],
            "decimal": [np.float64(2.5)],
        }
    )

    result = preview_data(df)

    assert isinstance(result.rows[0][0], int)
    assert not isinstance(result.rows[0][0], bool)
    assert isinstance(result.rows[0][1], float)


def test_preview_data_stringifies_unsupported_object_values() -> None:
    """Object không thuộc nhóm primitive được fallback thành chuỗi."""

    class CustomValue:
        def __str__(self) -> str:
            return "custom-value"

    result = preview_data(pd.DataFrame({"value": [CustomValue()]}))

    assert result.rows == [["custom-value"]]


@pytest.mark.parametrize("max_rows", [0, -1, True, "5"])
def test_preview_data_rejects_invalid_max_rows(max_rows) -> None:
    """max_rows phải là số nguyên dương và không được là bool."""

    with pytest.raises(InvalidConfigurationError):
        preview_data(pd.DataFrame({"value": [1]}), max_rows=max_rows)


@pytest.mark.parametrize("max_columns", [0, -1, True, "20"])
def test_preview_data_rejects_invalid_max_columns(max_columns) -> None:
    """max_columns phải là None hoặc số nguyên dương và không được là bool."""

    with pytest.raises(InvalidConfigurationError):
        preview_data(pd.DataFrame({"value": [1]}), max_columns=max_columns)


def test_preview_data_rejects_non_dataframe_input() -> None:
    """preview_data từ chối input không phải pandas DataFrame."""

    invalid_dataframe = cast(Any, [1, 2, 3])

    with pytest.raises(InvalidDatasetError):
        preview_data(invalid_dataframe)


def test_preview_data_preserves_column_order() -> None:
    """Preview giữ nguyên thứ tự cột gốc và không tự sắp xếp."""

    df = pd.DataFrame({"z": [1], "a": [2], "m": [3]})

    result = preview_data(df)

    assert result.columns == ["z", "a", "m"]


def test_preview_data_preserves_row_order() -> None:
    """Preview lấy các dòng đầu theo thứ tự gốc và không tự sắp xếp."""

    df = pd.DataFrame({"id": [30, 10, 20]})

    result = preview_data(df, max_rows=2)

    assert result.rows == [[30], [10]]


def test_preview_data_does_not_modify_dataframe() -> None:
    """Preview không fill missing, đổi dtype, đổi tên hoặc sắp xếp DataFrame."""

    df = pd.DataFrame(
        [[1, np.nan, pd.Timestamp("2026-09-08")], [2, 3.0, pd.NaT]],
        columns=["id", "value", "created_at"],
    )
    before = df.copy(deep=True)
    before_columns = list(df.columns)

    preview_data(df)

    pd.testing.assert_frame_equal(df, before)
    assert list(df.columns) == before_columns


def test_preview_data_is_deterministic() -> None:
    """Cùng một input tạo ra cùng một preview qua nhiều lần gọi."""

    df = pd.DataFrame(
        {
            "id": [1, 2],
            "created_at": [pd.Timestamp("2026-09-08"), pd.NaT],
        }
    )

    first = preview_data(df)
    second = preview_data(df)

    assert first == second


def test_preview_data_result_is_json_serializable() -> None:
    """Kết quả preview có thể serialize thành JSON."""

    df = pd.DataFrame(
        {
            "created_at": [pd.Timestamp("2026-09-08"), pd.NaT],
            "value": [np.int64(10), np.nan],
        }
    )

    result = preview_data(df)

    payload = result.model_dump_json()

    assert isinstance(payload, str)
    json.loads(payload)


def test_get_shape_is_deterministic() -> None:
    """Cùng DataFrame phải tạo cùng shape result qua nhiều lần gọi."""

    dataframe = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": ["x", "y", "z"],
        }
    )

    first = get_shape(dataframe)
    second = get_shape(dataframe)

    assert first == second
