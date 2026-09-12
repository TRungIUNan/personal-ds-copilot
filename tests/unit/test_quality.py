"""
W01-T05 — Kiểm thử behavior chất lượng dữ liệu

Các test bên dưới xác minh contract, edge case, tính bất biến, khả năng
serialization và tính tất định của các quality tool.
"""

import json

import pandas as pd
import pytest

from src.tools.config import MissingSeverityConfig
from src.tools.exceptions import InvalidConfigurationError, InvalidDatasetError
from src.tools.quality import (
    check_cardinality,
    check_constant_columns,
    check_duplicates,
    check_missing,
    detect_id_candidates,
)

QUALITY_TOOLS = (
    check_missing,
    check_duplicates,
    check_cardinality,
    check_constant_columns,
    detect_id_candidates,
)


def _quality_payload(result):
    """Chuyển output quality sang cấu trúc JSON-compatible của Pydantic v2."""

    if isinstance(result, list):
        return [item.model_dump() for item in result]
    return result.model_dump()


def test_missing_report_contains_count_rate_and_severity(normal_dataframe) -> None:
    """Missing report cung cấp field bắt buộc với rate dạng numeric."""

    result = check_missing(normal_dataframe)

    assert len(result) == 4
    assert [item.column for item in result] == [
        "customer_id",
        "age",
        "city",
        "income",
    ]

    assert result[0].position == 0
    assert result[0].missing_count == 0
    assert result[0].missing_rate == 0.0
    assert result[0].severity == "none"

    assert result[1].position == 1
    assert result[1].missing_count == 2
    assert result[1].missing_rate == pytest.approx(0.2)
    assert result[1].severity == "medium"

    assert result[2].position == 2
    assert result[2].missing_count == 1
    assert result[2].missing_rate == pytest.approx(0.1)
    assert result[2].severity == "medium"

    assert result[3].position == 3
    assert result[3].missing_count == 3
    assert result[3].missing_rate == pytest.approx(0.3)
    assert result[3].severity == "high"


def test_missing_severity_uses_centralized_configuration(
    normal_dataframe,
) -> None:
    """Severity threshold được cung cấp bởi một configuration policy duy nhất."""

    config = MissingSeverityConfig(
        thresholds={
            "low": 0.0,
            "medium": 0.25,
            "high": 0.50,
            "critical": 0.75,
        }
    )

    result = check_missing(normal_dataframe, config=config)

    assert [item.severity for item in result] == [
        "none",
        "low",
        "low",
        "medium",
    ]


def test_duplicate_report_distinguishes_full_rows_and_candidate_key(
    duplicate_rows_dataframe,
) -> None:
    """Duplicate output tách evidence toàn dòng và evidence theo candidate key."""

    without_key = check_duplicates(duplicate_rows_dataframe)

    assert without_key.total_rows == 5
    assert without_key.full_row_duplicate_count == 1
    assert without_key.full_row_duplicate_rate == pytest.approx(0.2)
    assert without_key.candidate_key is None
    assert without_key.candidate_key_duplicate_count is None
    assert without_key.candidate_key_duplicate_rate is None

    with_key = check_duplicates(
        duplicate_rows_dataframe,
        candidate_key="customer_id",
    )

    assert with_key.candidate_key == ["customer_id"]
    assert with_key.candidate_key_duplicate_count == 2
    assert with_key.candidate_key_duplicate_rate == pytest.approx(0.4)
    assert with_key.full_row_duplicate_count == 1
    assert with_key.full_row_duplicate_rate == pytest.approx(0.2)


def test_cardinality_reports_unique_count_and_rate(
    high_cardinality_string_dataframe,
) -> None:
    """Cardinality output chứa fact count/rate mà không đưa ra semantic claim."""

    result = check_cardinality(high_cardinality_string_dataframe)

    assert len(result) == 3
    assert [item.column for item in result] == [
        "customer_code",
        "city",
        "segment",
    ]

    assert result[0].position == 0
    assert result[0].non_missing_count == 10
    assert result[0].unique_count == 10
    assert result[0].unique_rate == pytest.approx(1.0)

    assert result[1].position == 1
    assert result[1].non_missing_count == 10
    assert result[1].unique_count == 3
    assert result[1].unique_rate == pytest.approx(0.3)

    assert result[2].position == 2
    assert result[2].non_missing_count == 10
    assert result[2].unique_count == 1
    assert result[2].unique_rate == pytest.approx(0.1)


def test_constant_report_documents_all_null_convention(
    constant_column_dataframe,
    all_null_column_dataframe,
) -> None:
    """Behavior cột constant được nêu rõ cho cột thường và cột all-null."""

    constant_result = check_constant_columns(constant_column_dataframe)

    assert len(constant_result) == 2
    assert constant_result[0].position == 0
    assert constant_result[0].column == "segment"
    assert constant_result[0].total_rows == 4
    assert constant_result[0].non_missing_count == 4
    assert constant_result[0].unique_count == 1
    assert constant_result[0].is_all_null is False
    assert constant_result[0].is_constant is True

    assert constant_result[1].position == 1
    assert constant_result[1].column == "city"
    assert constant_result[1].total_rows == 4
    assert constant_result[1].non_missing_count == 4
    assert constant_result[1].unique_count == 3
    assert constant_result[1].is_all_null is False
    assert constant_result[1].is_constant is False

    all_null_result = check_constant_columns(all_null_column_dataframe)
    all_null_item = next(
        item for item in all_null_result if item.column == "all_null"
    )

    assert all_null_item.total_rows == 3
    assert all_null_item.non_missing_count == 0
    assert all_null_item.unique_count == 0
    assert all_null_item.is_all_null is True
    assert all_null_item.is_constant is False


def test_id_detection_reports_candidates_not_certainty(possible_id_dataframe) -> None:
    """ID detection cung cấp evidence và không bao giờ khẳng định identity chắc chắn."""

    result = detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )

    assert len(result) == 4
    assert [item.column for item in result] == [
        "customer_id",
        "city",
        "reference_code",
        "id",
    ]

    customer_id = result[0]
    assert customer_id.position == 0
    assert customer_id.total_rows == 5
    assert customer_id.non_missing_count == 5
    assert customer_id.missing_count == 0
    assert customer_id.missing_rate == 0.0
    assert customer_id.unique_count == 5
    assert customer_id.unique_rate == 1.0
    assert customer_id.name_hint_match is True
    assert customer_id.candidate is True

    city = result[1]
    assert city.position == 1
    assert city.non_missing_count == 5
    assert city.missing_count == 0
    assert city.unique_count == 3
    assert city.unique_rate == pytest.approx(0.6)
    assert city.name_hint_match is False
    assert city.candidate is False

    reference_code = result[2]
    assert reference_code.position == 2
    assert reference_code.non_missing_count == 4
    assert reference_code.missing_count == 1
    assert reference_code.missing_rate == pytest.approx(0.2)
    assert reference_code.unique_count == 4
    assert reference_code.unique_rate == pytest.approx(1.0)
    assert reference_code.candidate is False

    repeated_id = result[3]
    assert repeated_id.position == 3
    assert repeated_id.non_missing_count == 5
    assert repeated_id.missing_count == 0
    assert repeated_id.unique_count == 1
    assert repeated_id.unique_rate == pytest.approx(0.2)
    assert repeated_id.name_hint_match is True
    assert repeated_id.candidate is False


@pytest.mark.parametrize(
    "tool",
    QUALITY_TOOLS,
    ids=[tool.__name__ for tool in QUALITY_TOOLS],
)
@pytest.mark.parametrize(
    "invalid_input",
    [None, [], {}, 42],
    ids=["none", "list", "dict", "scalar"],
)
def test_quality_tools_reject_invalid_dataframe_input(tool, invalid_input) -> None:
    """Quality tool từ chối input không phải DataFrame với lỗi đã document."""

    with pytest.raises(InvalidDatasetError):
        tool(invalid_input)


def test_quality_tools_do_not_modify_source_dataframe(normal_dataframe) -> None:
    """Quality tool giữ nguyên content và structure của DataFrame nguồn."""

    snapshot = normal_dataframe.copy(deep=True)

    for tool in QUALITY_TOOLS:
        tool(normal_dataframe)
        pd.testing.assert_frame_equal(normal_dataframe, snapshot)


def test_quality_outputs_are_json_serializable_and_deterministic(normal_dataframe) -> None:
    """Quality result serialize được và lặp lại chính xác với cùng input/config."""

    for tool in QUALITY_TOOLS:
        first_payload = _quality_payload(tool(normal_dataframe))
        second_payload = _quality_payload(tool(normal_dataframe))

        assert first_payload == second_payload
        json.dumps(first_payload)


# ============================================================
# check_missing
# ============================================================


def test_check_missing_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả về danh sách kết quả rỗng."""

    assert check_missing(pd.DataFrame()) == []


def test_check_missing_handles_zero_rows_with_columns() -> None:
    """DataFrame không có dòng vẫn giữ cột và dùng rate None."""

    dataframe = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "name": pd.Series(dtype="string"),
        }
    )

    result = check_missing(dataframe)

    assert [(item.position, item.column) for item in result] == [
        (0, "id"),
        (1, "name"),
    ]
    assert all(item.missing_count == 0 for item in result)
    assert all(item.missing_rate is None for item in result)
    assert all(item.severity == "none" for item in result)


def test_check_missing_handles_all_null_column() -> None:
    """Cột toàn null có rate 1.0 và severity critical."""

    result = check_missing(
        pd.DataFrame({"value": [None, None, None, None]})
    )

    assert result[0].missing_count == 4
    assert result[0].missing_rate == 1.0
    assert result[0].severity == "critical"


def test_check_missing_handles_column_without_missing_values() -> None:
    """Cột không có missing có rate 0.0 và severity none."""

    result = check_missing(pd.DataFrame({"value": [1, 2, 3, 4]}))

    assert result[0].missing_count == 0
    assert result[0].missing_rate == 0.0
    assert result[0].severity == "none"


def test_check_missing_uses_pandas_null_semantics() -> None:
    """None, NaN và pd.NA đều được tính là missing."""

    result = check_missing(
        pd.DataFrame({"value": [None, float("nan"), pd.NA, 10]})
    )

    assert result[0].missing_count == 3
    assert result[0].missing_rate == pytest.approx(0.75)
    assert result[0].severity == "critical"


def test_check_missing_handles_datetime_nat() -> None:
    """NaT trong cột datetime được tính theo null semantics của pandas."""

    dataframe = pd.DataFrame(
        {
            "created_at": [
                pd.Timestamp("2026-01-01"),
                pd.NaT,
                pd.Timestamp("2026-01-03"),
            ]
        }
    )

    result = check_missing(dataframe)

    assert result[0].missing_count == 1
    assert result[0].missing_rate == pytest.approx(1 / 3)
    assert result[0].severity == "high"


def test_check_missing_handles_nullable_boolean() -> None:
    """Boolean nullable với một giá trị thiếu được phân loại medium."""

    dataframe = pd.DataFrame(
        {
            "active": pd.Series(
                [True, None, False, True],
                dtype="boolean",
            )
        }
    )

    result = check_missing(dataframe)

    assert result[0].missing_count == 1
    assert result[0].missing_rate == pytest.approx(0.25)
    assert result[0].severity == "medium"


def test_check_missing_preserves_duplicate_columns_by_position() -> None:
    """Tên cột trùng vẫn tạo kết quả riêng theo từng position."""

    dataframe = pd.DataFrame(
        [[1, None], [None, 2], [3, None]],
        columns=["value", "value"],
    )

    result = check_missing(dataframe)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "value"
    assert result[0].missing_count == 1
    assert result[1].position == 1
    assert result[1].column == "value"
    assert result[1].missing_count == 2


def test_check_missing_handles_empty_column_name() -> None:
    """Tên cột rỗng vẫn được báo cáo mà không tạo warning tại tool này."""

    result = check_missing(pd.DataFrame([[1], [None]], columns=[""]))

    assert result[0].column == ""
    assert result[0].missing_count == 1
    assert result[0].missing_rate == pytest.approx(0.5)


def test_check_missing_serializes_non_string_column_label() -> None:
    """Nhãn cột không phải chuỗi được biểu diễn bằng str()."""

    result = check_missing(pd.DataFrame({123: [1, None, 3]}))

    assert result[0].column == "123"
    assert result[0].position == 0
    assert result[0].missing_count == 1


@pytest.mark.parametrize(
    "dataframe",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
)
def test_check_missing_rejects_non_dataframe_input(dataframe) -> None:
    """Input không phải DataFrame bị từ chối bằng lỗi typed."""

    with pytest.raises(InvalidDatasetError):
        check_missing(dataframe)


def test_check_missing_rejects_invalid_configuration(normal_dataframe) -> None:
    """Config không hợp lệ bị từ chối trước khi tạo report."""

    config = MissingSeverityConfig(thresholds={})

    with pytest.raises(InvalidConfigurationError):
        check_missing(normal_dataframe, config=config)


def test_check_missing_validates_config_for_empty_dataframe() -> None:
    """Config vẫn được validate với DataFrame 0x0."""

    config = MissingSeverityConfig(thresholds={})

    with pytest.raises(InvalidConfigurationError):
        check_missing(pd.DataFrame(), config=config)


def test_check_missing_validates_config_for_zero_row_dataframe() -> None:
    """Config vẫn được validate khi DataFrame có cột nhưng không có dòng."""

    dataframe = pd.DataFrame({"id": pd.Series(dtype="int64")})
    config = MissingSeverityConfig(thresholds={})

    with pytest.raises(InvalidConfigurationError):
        check_missing(dataframe, config=config)


def test_check_missing_does_not_modify_dataframe(normal_dataframe) -> None:
    """check_missing không thay đổi content, columns hoặc dtype nguồn."""

    before = normal_dataframe.copy(deep=True)
    before_columns = list(normal_dataframe.columns)
    before_dtypes = normal_dataframe.dtypes.copy()

    check_missing(normal_dataframe)

    pd.testing.assert_frame_equal(normal_dataframe, before)
    assert list(normal_dataframe.columns) == before_columns
    assert normal_dataframe.dtypes.equals(before_dtypes)


def test_check_missing_is_deterministic(normal_dataframe) -> None:
    """Cùng input tạo ra kết quả giống nhau qua nhiều lần gọi."""

    first = check_missing(normal_dataframe)
    second = check_missing(normal_dataframe)

    assert first == second


def test_check_missing_output_is_json_serializable(normal_dataframe) -> None:
    """Danh sách MissingColumnResult có thể serialize thành JSON."""

    result = check_missing(normal_dataframe)
    payload = [
        item.model_dump()
        for item in result
    ]
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    json.loads(serialized)


# ============================================================
# check_constant_columns
# ============================================================


def test_check_constant_columns_ignores_missing_when_evaluating_constant() -> None:
    """Missing không được tính là distinct value khi đánh giá constant."""

    result = check_constant_columns(
        pd.DataFrame({"value": ["A", "A", None, None]})
    )

    assert result[0].total_rows == 4
    assert result[0].non_missing_count == 2
    assert result[0].unique_count == 1
    assert result[0].is_all_null is False
    assert result[0].is_constant is True


def test_check_constant_columns_identifies_non_constant_column() -> None:
    """Cột có nhiều hơn một observed value không phải constant."""

    result = check_constant_columns(
        pd.DataFrame({"value": ["A", "B", "A", "B"]})
    )

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 2
    assert result[0].is_all_null is False
    assert result[0].is_constant is False


def test_check_constant_columns_handles_all_null_column() -> None:
    """Cột có dòng nhưng toàn null là all-null, không phải constant."""

    result = check_constant_columns(
        pd.DataFrame({"value": [None, None, None]})
    )

    assert result[0].total_rows == 3
    assert result[0].non_missing_count == 0
    assert result[0].unique_count == 0
    assert result[0].is_all_null is True
    assert result[0].is_constant is False


def test_check_constant_columns_handles_zero_rows_with_columns() -> None:
    """Zero-row column không bị coi là all-null hoặc constant."""

    dataframe = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "segment": pd.Series(dtype="string"),
        }
    )

    result = check_constant_columns(dataframe)

    assert len(result) == 2
    assert [(item.position, item.column) for item in result] == [
        (0, "id"),
        (1, "segment"),
    ]
    assert all(item.total_rows == 0 for item in result)
    assert all(item.non_missing_count == 0 for item in result)
    assert all(item.unique_count == 0 for item in result)
    assert all(item.is_all_null is False for item in result)
    assert all(item.is_constant is False for item in result)


def test_check_constant_columns_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả về danh sách rỗng."""

    assert check_constant_columns(pd.DataFrame()) == []


def test_check_constant_columns_treats_single_observed_value_as_constant() -> None:
    """Một observed distinct value được coi là constant."""

    result = check_constant_columns(pd.DataFrame({"value": ["A"]}))

    assert result[0].total_rows == 1
    assert result[0].non_missing_count == 1
    assert result[0].unique_count == 1
    assert result[0].is_all_null is False
    assert result[0].is_constant is True


def test_check_constant_columns_treats_single_observed_value_with_missing_as_constant() -> None:
    """Một observed value cùng nhiều missing vẫn là constant."""

    result = check_constant_columns(
        pd.DataFrame({"value": [None, "A", None, None]})
    )

    assert result[0].total_rows == 4
    assert result[0].non_missing_count == 1
    assert result[0].unique_count == 1
    assert result[0].is_all_null is False
    assert result[0].is_constant is True


def test_check_constant_columns_handles_fully_unique_column() -> None:
    """Cột có mọi observed value khác nhau không phải constant."""

    result = check_constant_columns(pd.DataFrame({"id": [1, 2, 3, 4]}))

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 4
    assert result[0].is_all_null is False
    assert result[0].is_constant is False


def test_check_constant_columns_handles_datetime_column() -> None:
    """Datetime duplicate và NaT được xử lý theo quy ước non-missing."""

    dataframe = pd.DataFrame(
        {
            "date": [
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2026-01-01"),
                pd.NaT,
            ]
        }
    )

    result = check_constant_columns(dataframe)

    assert result[0].total_rows == 3
    assert result[0].non_missing_count == 2
    assert result[0].unique_count == 1
    assert result[0].is_all_null is False
    assert result[0].is_constant is True


def test_check_constant_columns_handles_nullable_boolean() -> None:
    """Boolean nullable với một observed value là constant."""

    dataframe = pd.DataFrame(
        {
            "flag": pd.Series(
                [True, True, None, True],
                dtype="boolean",
            )
        }
    )

    result = check_constant_columns(dataframe)

    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 1
    assert result[0].is_all_null is False
    assert result[0].is_constant is True


def test_check_constant_columns_handles_mixed_hashable_values() -> None:
    """Mixed hashable values khác nhau không bị ép chuyển dtype."""

    result = check_constant_columns(
        pd.DataFrame({"value": [1, "1", 1, "1"]})
    )

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 2
    assert result[0].is_constant is False


def test_check_constant_columns_preserves_duplicate_columns_by_position() -> None:
    """Duplicate column labels vẫn tạo result riêng theo position."""

    dataframe = pd.DataFrame(
        [
            ["A", 1],
            ["A", 2],
            ["A", 2],
        ],
        columns=["value", "value"],
    )

    result = check_constant_columns(dataframe)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "value"
    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 1
    assert result[0].is_constant is True
    assert result[1].position == 1
    assert result[1].column == "value"
    assert result[1].non_missing_count == 3
    assert result[1].unique_count == 2
    assert result[1].is_constant is False


def test_check_constant_columns_handles_empty_column_name() -> None:
    """Tên cột rỗng vẫn được biểu diễn đúng trong result."""

    result = check_constant_columns(
        pd.DataFrame([["A"], ["A"], [None]], columns=[""])
    )

    assert result[0].position == 0
    assert result[0].column == ""
    assert result[0].non_missing_count == 2
    assert result[0].unique_count == 1
    assert result[0].is_constant is True


def test_check_constant_columns_serializes_non_string_column_label() -> None:
    """Nhãn cột không phải string được chuyển thành str()."""

    result = check_constant_columns(pd.DataFrame({123: ["A", "A", "A"]}))

    assert result[0].position == 0
    assert result[0].column == "123"
    assert result[0].unique_count == 1
    assert result[0].is_constant is True


@pytest.mark.parametrize(
    "dataframe",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
)
def test_check_constant_columns_rejects_non_dataframe_input(dataframe) -> None:
    """Input không phải DataFrame bị từ chối bằng InvalidDatasetError."""

    with pytest.raises(InvalidDatasetError):
        check_constant_columns(dataframe)


def test_check_constant_columns_rejects_unhashable_values() -> None:
    """List chỉ test lỗi nếu pandas nunique raise TypeError."""

    dataframe = pd.DataFrame(
        {
            "payload": [
                [1, 2],
                [1, 2],
            ]
        }
    )

    try:
        dataframe["payload"].nunique(dropna=True)
    except TypeError:
        pass
    else:
        pytest.skip(
            "Phiên bản pandas hiện tại hỗ trợ value này trong nunique()."
        )

    with pytest.raises(InvalidDatasetError):
        check_constant_columns(dataframe)


def test_check_constant_columns_does_not_modify_dataframe(
    constant_column_dataframe,
) -> None:
    """check_constant_columns không thay đổi content, columns hoặc dtype nguồn."""

    before = constant_column_dataframe.copy(deep=True)
    before_columns = list(constant_column_dataframe.columns)
    before_dtypes = constant_column_dataframe.dtypes.copy()

    check_constant_columns(constant_column_dataframe)

    pd.testing.assert_frame_equal(constant_column_dataframe, before)
    assert list(constant_column_dataframe.columns) == before_columns
    assert constant_column_dataframe.dtypes.equals(before_dtypes)


def test_check_constant_columns_is_deterministic(
    constant_column_dataframe,
) -> None:
    """Cùng input tạo ra kết quả giống nhau qua nhiều lần gọi."""

    first = check_constant_columns(constant_column_dataframe)
    second = check_constant_columns(constant_column_dataframe)

    assert first == second


def test_check_constant_columns_output_is_json_serializable(
    constant_column_dataframe,
) -> None:
    """Danh sách ConstantColumnResult có thể serialize thành JSON."""

    result = check_constant_columns(constant_column_dataframe)
    payload = [
        item.model_dump()
        for item in result
    ]
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    json.loads(serialized)


def test_check_constant_columns_boolean_fields_are_booleans(
    constant_column_dataframe,
) -> None:
    """Hai field trạng thái phải là bool thật, không phải chuỗi."""

    result = check_constant_columns(constant_column_dataframe)

    for item in result:
        assert isinstance(item.is_all_null, bool)
        assert isinstance(item.is_constant, bool)


# ============================================================
# check_cardinality
# ============================================================


def test_check_cardinality_excludes_missing_values_from_unique_count() -> None:
    """Missing không được tính vào unique count hoặc denominator."""

    result = check_cardinality(
        pd.DataFrame({"city": ["HN", "HN", "HCM", None]})
    )

    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(2 / 3)


def test_check_cardinality_uses_pandas_null_semantics() -> None:
    """None, NaN và pd.NA đều được loại khỏi cardinality."""

    result = check_cardinality(
        pd.DataFrame({"value": ["A", None, float("nan"), pd.NA, "B"]})
    )

    assert result[0].non_missing_count == 2
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(1.0)


def test_check_cardinality_handles_all_null_column() -> None:
    """Cột toàn null có count zero và rate None."""

    result = check_cardinality(
        pd.DataFrame({"value": [None, None, None]})
    )

    assert result[0].non_missing_count == 0
    assert result[0].unique_count == 0
    assert result[0].unique_rate is None


def test_check_cardinality_handles_zero_rows_with_columns() -> None:
    """Zero-row DataFrame giữ đúng position, column và quy ước rate None."""

    dataframe = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "city": pd.Series(dtype="string"),
        }
    )

    result = check_cardinality(dataframe)

    assert len(result) == 2
    assert [(item.position, item.column) for item in result] == [
        (0, "id"),
        (1, "city"),
    ]
    assert all(item.non_missing_count == 0 for item in result)
    assert all(item.unique_count == 0 for item in result)
    assert all(item.unique_rate is None for item in result)


def test_check_cardinality_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả về danh sách rỗng."""

    assert check_cardinality(pd.DataFrame()) == []


def test_check_cardinality_handles_constant_column() -> None:
    """Cột constant có một unique value và rate theo non-missing count."""

    result = check_cardinality(
        pd.DataFrame({"segment": ["A", "A", "A", "A"]})
    )

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 1
    assert result[0].unique_rate == pytest.approx(0.25)


def test_check_cardinality_handles_fully_unique_column() -> None:
    """Cột fully unique có unique rate bằng 1.0."""

    result = check_cardinality(
        pd.DataFrame({"id": [101, 102, 103, 104]})
    )

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 4
    assert result[0].unique_rate == pytest.approx(1.0)


def test_check_cardinality_uses_non_missing_denominator() -> None:
    """Unique rate dùng non_missing_count, không dùng tổng số dòng."""

    result = check_cardinality(
        pd.DataFrame({"value": ["A", None, None, None]})
    )

    assert result[0].non_missing_count == 1
    assert result[0].unique_count == 1
    assert result[0].unique_rate == pytest.approx(1.0)


def test_check_cardinality_handles_datetime_column() -> None:
    """Datetime duplicate và NaT được tính đúng."""

    dataframe = pd.DataFrame(
        {
            "date": [
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2026-01-02"),
                pd.NaT,
            ]
        }
    )

    result = check_cardinality(dataframe)

    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(2 / 3)


def test_check_cardinality_handles_nullable_boolean() -> None:
    """Boolean nullable bỏ giá trị thiếu khi tính cardinality."""

    dataframe = pd.DataFrame(
        {
            "flag": pd.Series(
                [True, False, True, None],
                dtype="boolean",
            )
        }
    )

    result = check_cardinality(dataframe)

    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(2 / 3)


def test_check_cardinality_handles_mixed_hashable_values() -> None:
    """Các giá trị hashable khác kiểu vẫn được đếm distinct ổn định."""

    result = check_cardinality(
        pd.DataFrame({"value": [1, "1", 1, "1", None]})
    )

    assert result[0].non_missing_count == 4
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(0.5)


def test_check_cardinality_preserves_duplicate_columns_by_position() -> None:
    """Tên cột trùng vẫn tạo result riêng theo từng vị trí."""

    dataframe = pd.DataFrame(
        [
            ["A", 1],
            ["A", 2],
            ["B", 2],
        ],
        columns=["value", "value"],
    )

    result = check_cardinality(dataframe)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "value"
    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(2 / 3)
    assert result[1].position == 1
    assert result[1].column == "value"
    assert result[1].non_missing_count == 3
    assert result[1].unique_count == 2
    assert result[1].unique_rate == pytest.approx(2 / 3)


def test_check_cardinality_handles_empty_column_name() -> None:
    """Tên cột rỗng vẫn được biểu diễn chính xác trong result."""

    result = check_cardinality(
        pd.DataFrame([["A"], ["B"], ["A"]], columns=[""])
    )

    assert result[0].position == 0
    assert result[0].column == ""
    assert result[0].non_missing_count == 3
    assert result[0].unique_count == 2
    assert result[0].unique_rate == pytest.approx(2 / 3)


def test_check_cardinality_serializes_non_string_column_label() -> None:
    """Nhãn cột không phải string được chuyển thành str()."""

    result = check_cardinality(pd.DataFrame({123: ["A", "B", "A"]}))

    assert result[0].position == 0
    assert result[0].column == "123"
    assert result[0].unique_count == 2


@pytest.mark.parametrize(
    "dataframe",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
)
def test_check_cardinality_rejects_non_dataframe_input(dataframe) -> None:
    """Input không phải DataFrame bị từ chối bằng InvalidDatasetError."""

    with pytest.raises(InvalidDatasetError):
        check_cardinality(dataframe)


def test_check_cardinality_rejects_unhashable_values() -> None:
    """Giá trị list chỉ test lỗi nếu pandas nunique raise TypeError."""

    dataframe = pd.DataFrame({"payload": [[1, 2], [1, 2]]})

    try:
        dataframe["payload"].nunique(dropna=True)
    except TypeError:
        pass
    else:
        pytest.skip(
            "Phiên bản pandas hiện tại hỗ trợ value này trong nunique()."
        )

    with pytest.raises(InvalidDatasetError):
        check_cardinality(dataframe)


def test_check_cardinality_does_not_modify_dataframe(
    high_cardinality_string_dataframe,
) -> None:
    """check_cardinality không thay đổi content, columns hoặc dtype nguồn."""

    before = high_cardinality_string_dataframe.copy(deep=True)
    before_columns = list(high_cardinality_string_dataframe.columns)
    before_dtypes = high_cardinality_string_dataframe.dtypes.copy()

    check_cardinality(high_cardinality_string_dataframe)

    pd.testing.assert_frame_equal(high_cardinality_string_dataframe, before)
    assert list(high_cardinality_string_dataframe.columns) == before_columns
    assert high_cardinality_string_dataframe.dtypes.equals(before_dtypes)


def test_check_cardinality_is_deterministic(
    high_cardinality_string_dataframe,
) -> None:
    """Cùng input tạo ra kết quả giống nhau qua nhiều lần gọi."""

    first = check_cardinality(high_cardinality_string_dataframe)
    second = check_cardinality(high_cardinality_string_dataframe)

    assert first == second


def test_check_cardinality_output_is_json_serializable(
    high_cardinality_string_dataframe,
) -> None:
    """Danh sách CardinalityResult có thể serialize thành JSON."""

    result = check_cardinality(high_cardinality_string_dataframe)
    payload = [
        item.model_dump()
        for item in result
    ]
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    json.loads(serialized)


def test_check_cardinality_rates_are_bounded(
    high_cardinality_string_dataframe,
) -> None:
    """Mọi unique rate được trả về đều nằm trong khoảng 0.0 đến 1.0."""

    result = check_cardinality(high_cardinality_string_dataframe)

    for item in result:
        if item.unique_rate is not None:
            assert 0.0 <= item.unique_rate <= 1.0


# ============================================================
# check_duplicates
# ============================================================


def test_check_duplicates_supports_composite_candidate_key(
    duplicate_rows_dataframe,
) -> None:
    """Candidate key ghép giữ thứ tự và đếm duplicate theo toàn bộ key."""

    result = check_duplicates(
        duplicate_rows_dataframe,
        candidate_key=["customer_id", "city"],
    )

    assert result.candidate_key == ["customer_id", "city"]
    assert result.candidate_key_duplicate_count == 1
    assert result.candidate_key_duplicate_rate == pytest.approx(0.2)


def test_check_duplicates_handles_dataframe_without_duplicates() -> None:
    """DataFrame không có duplicate có count và rate bằng zero."""

    dataframe = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "city": ["HN", "HCM", "DN"],
        }
    )

    without_key = check_duplicates(dataframe)
    with_key = check_duplicates(dataframe, candidate_key="id")

    assert without_key.total_rows == 3
    assert without_key.full_row_duplicate_count == 0
    assert without_key.full_row_duplicate_rate == 0.0
    assert without_key.candidate_key is None
    assert without_key.candidate_key_duplicate_count is None
    assert without_key.candidate_key_duplicate_rate is None
    assert with_key.candidate_key_duplicate_count == 0
    assert with_key.candidate_key_duplicate_rate == 0.0


def test_check_duplicates_handles_empty_dataframe() -> None:
    """DataFrame 0x0 có count zero và rate None."""

    result = check_duplicates(pd.DataFrame())

    assert result.total_rows == 0
    assert result.full_row_duplicate_count == 0
    assert result.full_row_duplicate_rate is None
    assert result.candidate_key is None
    assert result.candidate_key_duplicate_count is None
    assert result.candidate_key_duplicate_rate is None


def test_check_duplicates_handles_zero_rows_with_candidate_key() -> None:
    """Zero-row DataFrame vẫn normalize key và không tạo duplicate."""

    dataframe = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "city": pd.Series(dtype="string"),
        }
    )

    result = check_duplicates(dataframe, candidate_key="id")

    assert result.total_rows == 0
    assert result.full_row_duplicate_count == 0
    assert result.full_row_duplicate_rate is None
    assert result.candidate_key == ["id"]
    assert result.candidate_key_duplicate_count == 0
    assert result.candidate_key_duplicate_rate is None


def test_check_duplicates_counts_only_occurrences_after_first() -> None:
    """Mỗi nhóm giống nhau chỉ tính occurrence sau bản đầu tiên."""

    dataframe = pd.DataFrame(
        {
            "a": [1, 1, 1, 1],
            "b": ["x", "x", "x", "x"],
        }
    )

    result = check_duplicates(dataframe, candidate_key="a")

    assert result.total_rows == 4
    assert result.full_row_duplicate_count == 3
    assert result.full_row_duplicate_rate == pytest.approx(0.75)
    assert result.candidate_key_duplicate_count == 3
    assert result.candidate_key_duplicate_rate == pytest.approx(0.75)


def test_check_duplicates_handles_single_row_dataframe() -> None:
    """DataFrame một dòng không có duplicate."""

    dataframe = pd.DataFrame({"id": [1], "city": ["HN"]})

    result = check_duplicates(dataframe, candidate_key="id")

    assert result.full_row_duplicate_count == 0
    assert result.full_row_duplicate_rate == 0.0
    assert result.candidate_key_duplicate_count == 0
    assert result.candidate_key_duplicate_rate == 0.0


def test_check_duplicates_normalizes_string_candidate_key_to_list() -> None:
    """Candidate key dạng string được trả về dưới dạng list một phần tử."""

    result = check_duplicates(
        pd.DataFrame({"id": [1, 2]}),
        candidate_key="id",
    )

    assert result.candidate_key == ["id"]


def test_check_duplicates_preserves_candidate_key_order() -> None:
    """Thứ tự composite key được giữ nguyên theo caller."""

    dataframe = pd.DataFrame(
        {
            "id": [1, 2],
            "date": ["2026-01-01", "2026-01-02"],
            "city": ["HN", "HCM"],
        }
    )

    result = check_duplicates(dataframe, candidate_key=["date", "id"])

    assert result.candidate_key == ["date", "id"]


def test_check_duplicates_rejects_empty_candidate_key() -> None:
    """Candidate key rỗng không phải configuration hợp lệ."""

    dataframe = pd.DataFrame({"id": [1, 2]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=[])


@pytest.mark.parametrize("candidate_key", [123, 3.14, True])
def test_check_duplicates_rejects_non_iterable_candidate_key(candidate_key) -> None:
    """Candidate key phải là string hoặc iterable hợp lệ."""

    dataframe = pd.DataFrame({"id": [1, 2]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=candidate_key)


@pytest.mark.parametrize(
    "candidate_key",
    [[1], ["id", 2], [None]],
)
def test_check_duplicates_rejects_non_string_candidate_key_elements(
    candidate_key,
) -> None:
    """Mọi phần tử của candidate key phải là string."""

    dataframe = pd.DataFrame({"id": [1, 2]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=candidate_key)


@pytest.mark.parametrize("candidate_key", ["", [""]])
def test_check_duplicates_rejects_empty_string_candidate_key(candidate_key) -> None:
    """Tên cột rỗng không phải candidate key hợp lệ."""

    dataframe = pd.DataFrame({"id": [1, 2]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=candidate_key)


def test_check_duplicates_rejects_duplicate_candidate_key_names() -> None:
    """Một cột không được xuất hiện nhiều lần trong composite key."""

    dataframe = pd.DataFrame({"id": [1, 2]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=["id", "id"])


def test_check_duplicates_rejects_missing_candidate_key_column() -> None:
    """Tên cột không tồn tại phải trả về InvalidConfigurationError."""

    dataframe = pd.DataFrame({"id": [1, 2, 3]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key="customer_id")


def test_check_duplicates_rejects_composite_key_with_missing_column() -> None:
    """Composite key có một cột không tồn tại phải bị từ chối."""

    dataframe = pd.DataFrame({"id": [1, 2], "city": ["HN", "HCM"]})

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key=["id", "date"])


def test_check_duplicates_rejects_ambiguous_candidate_key_label() -> None:
    """Candidate key không thể lookup mơ hồ trên duplicate column label."""

    dataframe = pd.DataFrame(
        [[1, 10], [2, 20]],
        columns=["id", "id"],
    )

    with pytest.raises(InvalidConfigurationError):
        check_duplicates(dataframe, candidate_key="id")


def test_check_duplicates_allows_duplicate_column_labels_without_candidate_key() -> None:
    """Duplicate label chỉ mơ hồ với key, không chặn full-row mode."""

    dataframe = pd.DataFrame(
        [[1, 10], [1, 10]],
        columns=["value", "value"],
    )

    result = check_duplicates(dataframe)

    assert result.full_row_duplicate_count == 1
    assert result.full_row_duplicate_rate == pytest.approx(0.5)
    assert result.candidate_key is None


def test_check_duplicates_uses_pandas_null_semantics_for_candidate_key() -> None:
    """Null trong key không bị drop và tuân theo duplicated của pandas."""

    dataframe = pd.DataFrame(
        {
            "id": [1, None, None, 2],
            "value": ["a", "b", "c", "d"],
        }
    )

    result = check_duplicates(dataframe, candidate_key="id")

    assert result.candidate_key_duplicate_count == 1
    assert result.candidate_key_duplicate_rate == pytest.approx(0.25)


def test_check_duplicates_handles_nulls_in_composite_candidate_key() -> None:
    """Null trong composite key vẫn được tính theo tuple key của pandas."""

    dataframe = pd.DataFrame(
        {
            "id": [1, 1, 1, 2],
            "code": [None, None, "A", None],
        }
    )

    result = check_duplicates(
        dataframe,
        candidate_key=["id", "code"],
    )

    assert result.candidate_key_duplicate_count == 1
    assert result.candidate_key_duplicate_rate == pytest.approx(0.25)


@pytest.mark.parametrize(
    "dataframe",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
)
def test_check_duplicates_rejects_non_dataframe_input(dataframe) -> None:
    """Input không phải DataFrame bị từ chối bằng InvalidDatasetError."""

    with pytest.raises(InvalidDatasetError):
        check_duplicates(dataframe)


def test_check_duplicates_rejects_unhashable_full_row_values() -> None:
    """Full-row duplicate với list chỉ test khi pandas thực sự raise TypeError."""

    dataframe = pd.DataFrame(
        {
            "id": [1, 1],
            "payload": [[1, 2], [1, 2]],
        }
    )

    try:
        dataframe.duplicated()
    except TypeError:
        pass
    else:
        pytest.skip("Phiên bản pandas hiện tại hỗ trợ list khi duplicated().")

    with pytest.raises(InvalidDatasetError):
        check_duplicates(dataframe)


def test_check_duplicates_rejects_unhashable_candidate_key_values() -> None:
    """Candidate-key duplicate với list chỉ test khi pandas raise TypeError."""

    dataframe = pd.DataFrame(
        {
            "payload": [[1], [1]],
            "other": [10, 20],
        }
    )

    try:
        dataframe.duplicated(subset=["payload"])
    except TypeError:
        pass
    else:
        pytest.skip(
            "Phiên bản pandas hiện tại hỗ trợ list khi duplicated(subset=...)."
        )

    with pytest.raises(InvalidDatasetError):
        check_duplicates(dataframe, candidate_key="payload")


def test_check_duplicates_does_not_modify_dataframe(duplicate_rows_dataframe) -> None:
    """check_duplicates không thay đổi content, columns hoặc dtype nguồn."""

    before = duplicate_rows_dataframe.copy(deep=True)
    before_columns = list(duplicate_rows_dataframe.columns)
    before_dtypes = duplicate_rows_dataframe.dtypes.copy()

    check_duplicates(
        duplicate_rows_dataframe,
        candidate_key="customer_id",
    )

    pd.testing.assert_frame_equal(duplicate_rows_dataframe, before)
    assert list(duplicate_rows_dataframe.columns) == before_columns
    assert duplicate_rows_dataframe.dtypes.equals(before_dtypes)


def test_check_duplicates_is_deterministic(duplicate_rows_dataframe) -> None:
    """Cùng input và candidate key tạo ra kết quả giống nhau."""

    first = check_duplicates(
        duplicate_rows_dataframe,
        candidate_key=["customer_id", "city"],
    )
    second = check_duplicates(
        duplicate_rows_dataframe,
        candidate_key=["customer_id", "city"],
    )

    assert first == second


def test_check_duplicates_output_is_json_serializable(duplicate_rows_dataframe) -> None:
    """DuplicateReport có thể serialize thành JSON."""

    result = check_duplicates(
        duplicate_rows_dataframe,
        candidate_key="customer_id",
    )
    payload = result.model_dump()
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    json.loads(serialized)


# ============================================================
# detect_id_candidates
# ============================================================


def test_detect_id_candidates_name_hint_does_not_force_candidate() -> None:
    """Name hint là evidence yếu và không thay thế dữ liệu quan sát."""

    result = detect_id_candidates(
        pd.DataFrame({"id": [1, 1, 1, 1]}),
        column_name_hints=["id"],
    )

    assert result[0].name_hint_match is True
    assert result[0].unique_count == 1
    assert result[0].candidate is False


def test_detect_id_candidates_can_flag_unique_column_without_name_hint() -> None:
    """Cột unique vẫn có thể là candidate khi không có name hint."""

    result = detect_id_candidates(pd.DataFrame({"age": [20, 21, 22, 23]}))

    assert result[0].name_hint_match is False
    assert result[0].missing_count == 0
    assert result[0].unique_count == 4
    assert result[0].unique_rate == 1.0
    assert result[0].candidate is True


def test_detect_id_candidates_rejects_candidate_with_missing_values() -> None:
    """Cột có missing không được đánh dấu candidate dù observed values unique."""

    result = detect_id_candidates(
        pd.DataFrame({"reference": ["R1", "R2", None, "R4"]})
    )

    assert result[0].non_missing_count == 3
    assert result[0].missing_count == 1
    assert result[0].missing_rate == pytest.approx(0.25)
    assert result[0].unique_count == 3
    assert result[0].unique_rate == pytest.approx(1.0)
    assert result[0].candidate is False


def test_detect_id_candidates_rejects_non_unique_column() -> None:
    """Cột không unique không được đánh dấu candidate."""

    result = detect_id_candidates(
        pd.DataFrame({"code": ["A", "A", "B", "C"]})
    )

    assert result[0].missing_count == 0
    assert result[0].unique_count == 3
    assert result[0].unique_rate == pytest.approx(0.75)
    assert result[0].candidate is False


def test_detect_id_candidates_requires_at_least_two_rows() -> None:
    """Một dòng dù unique cũng không đủ điều kiện candidate."""

    result = detect_id_candidates(pd.DataFrame({"id": [1]}))

    assert result[0].total_rows == 1
    assert result[0].missing_count == 0
    assert result[0].unique_count == 1
    assert result[0].unique_rate == 1.0
    assert result[0].candidate is False


def test_detect_id_candidates_handles_zero_rows_with_columns() -> None:
    """Zero-row DataFrame giữ cột và dùng None cho các rate."""

    dataframe = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "code": pd.Series(dtype="string"),
        }
    )

    result = detect_id_candidates(dataframe)

    assert len(result) == 2
    assert [(item.position, item.column) for item in result] == [
        (0, "id"),
        (1, "code"),
    ]
    for item in result:
        assert item.total_rows == 0
        assert item.non_missing_count == 0
        assert item.missing_count == 0
        assert item.missing_rate is None
        assert item.unique_count == 0
        assert item.unique_rate is None
        assert item.candidate is False


def test_detect_id_candidates_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả về danh sách rỗng."""

    assert detect_id_candidates(pd.DataFrame()) == []


def test_detect_id_candidates_handles_all_null_column() -> None:
    """Cột all-null có hint nhưng không thể là candidate."""

    result = detect_id_candidates(
        pd.DataFrame({"id": [None, None, None]}),
        column_name_hints="id",
    )

    assert result[0].total_rows == 3
    assert result[0].non_missing_count == 0
    assert result[0].missing_count == 3
    assert result[0].missing_rate == 1.0
    assert result[0].unique_count == 0
    assert result[0].unique_rate is None
    assert result[0].name_hint_match is True
    assert result[0].candidate is False


def test_detect_id_candidates_matches_hints_case_insensitively() -> None:
    """Hint được so khớp exact theo casefold()."""

    result = detect_id_candidates(
        pd.DataFrame({"Customer_ID": [1, 2, 3]}),
        column_name_hints=["customer_id"],
    )

    assert result[0].name_hint_match is True


def test_detect_id_candidates_does_not_use_substring_hint_matching() -> None:
    """Hint không được match theo substring."""

    result = detect_id_candidates(
        pd.DataFrame({"customer_id": [1, 2, 3]}),
        column_name_hints=["id"],
    )

    assert result[0].name_hint_match is False
    assert result[0].candidate is True


def test_detect_id_candidates_accepts_single_string_hint() -> None:
    """Một hint dạng string được chấp nhận trực tiếp."""

    result = detect_id_candidates(
        pd.DataFrame({"id": [1, 2, 3]}),
        column_name_hints="id",
    )

    assert result[0].name_hint_match is True
    assert result[0].candidate is True


def test_detect_id_candidates_accepts_multiple_hints() -> None:
    """Nhiều hint được áp dụng độc lập cho từng cột."""

    dataframe = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "customer_code": ["C1", "C2", "C3"],
            "city": ["HN", "HCM", "DN"],
        }
    )

    result = detect_id_candidates(
        dataframe,
        column_name_hints=["id", "customer_code"],
    )

    assert result[0].name_hint_match is True
    assert result[1].name_hint_match is True
    assert result[2].name_hint_match is False


def test_detect_id_candidates_allows_duplicate_hints() -> None:
    """Duplicate hint không làm phát sinh lỗi."""

    result = detect_id_candidates(
        pd.DataFrame({"id": [1, 2, 3]}),
        column_name_hints=["id", "ID", "id"],
    )

    assert result[0].name_hint_match is True


@pytest.mark.parametrize("hints", [123, 3.14, True])
def test_detect_id_candidates_rejects_invalid_hint_container(hints) -> None:
    """Container hint phải là string hoặc iterable hợp lệ."""

    with pytest.raises(InvalidConfigurationError):
        detect_id_candidates(
            pd.DataFrame({"id": [1, 2]}),
            column_name_hints=hints,
        )


@pytest.mark.parametrize(
    "hints",
    [[1], ["id", 2], [None]],
)
def test_detect_id_candidates_rejects_non_string_hint_elements(hints) -> None:
    """Mọi phần tử trong iterable hint phải là string."""

    with pytest.raises(InvalidConfigurationError):
        detect_id_candidates(
            pd.DataFrame({"id": [1, 2]}),
            column_name_hints=hints,
        )


@pytest.mark.parametrize("hints", ["", [""], ["id", ""]])
def test_detect_id_candidates_rejects_empty_string_hint(hints) -> None:
    """Hint rỗng không phải configuration hợp lệ."""

    with pytest.raises(InvalidConfigurationError):
        detect_id_candidates(
            pd.DataFrame({"id": [1, 2]}),
            column_name_hints=hints,
        )


def test_detect_id_candidates_handles_datetime_column() -> None:
    """Datetime unique không missing có thể là candidate."""

    dataframe = pd.DataFrame(
        {
            "event_time": [
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2026-01-02"),
                pd.Timestamp("2026-01-03"),
            ]
        }
    )

    result = detect_id_candidates(dataframe)

    assert result[0].missing_count == 0
    assert result[0].unique_count == 3
    assert result[0].unique_rate == 1.0
    assert isinstance(result[0].dtype, str)
    assert result[0].dtype
    assert result[0].candidate is True


def test_detect_id_candidates_handles_nullable_boolean() -> None:
    """Nullable boolean có missing và không được đánh dấu candidate."""

    dataframe = pd.DataFrame(
        {
            "flag": pd.Series(
                [True, False, True, None],
                dtype="boolean",
            )
        }
    )

    result = detect_id_candidates(dataframe)

    assert result[0].non_missing_count == 3
    assert result[0].missing_count == 1
    assert result[0].unique_count == 2
    assert result[0].candidate is False


def test_detect_id_candidates_preserves_duplicate_columns_by_position() -> None:
    """Duplicate label vẫn được report cho từng physical column."""

    dataframe = pd.DataFrame(
        [
            [1, "A"],
            [2, "B"],
            [3, "C"],
        ],
        columns=["id", "id"],
    )

    result = detect_id_candidates(
        dataframe,
        column_name_hints=["id"],
    )

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "id"
    assert result[0].name_hint_match is True
    assert result[0].candidate is True
    assert result[1].position == 1
    assert result[1].column == "id"
    assert result[1].name_hint_match is True
    assert result[1].candidate is True


def test_detect_id_candidates_handles_empty_column_name_without_hints() -> None:
    """Nhãn cột rỗng được report; chỉ hint rỗng mới invalid."""

    result = detect_id_candidates(
        pd.DataFrame([[1], [2], [3]], columns=[""])
    )

    assert result[0].position == 0
    assert result[0].column == ""
    assert result[0].name_hint_match is False
    assert result[0].candidate is True


def test_detect_id_candidates_serializes_non_string_column_label() -> None:
    """Nhãn cột không phải string được chuyển thành str()."""

    result = detect_id_candidates(pd.DataFrame({123: [1, 2, 3]}))

    assert result[0].position == 0
    assert result[0].column == "123"
    assert result[0].candidate is True


@pytest.mark.parametrize(
    "dataframe",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
)
def test_detect_id_candidates_rejects_non_dataframe_input(dataframe) -> None:
    """Input không phải DataFrame bị từ chối bằng InvalidDatasetError."""

    with pytest.raises(InvalidDatasetError):
        detect_id_candidates(dataframe)


def test_detect_id_candidates_rejects_unhashable_values() -> None:
    """List chỉ test lỗi nếu pandas nunique raise TypeError."""

    dataframe = pd.DataFrame(
        {
            "payload": [
                [1, 2],
                [1, 2],
            ]
        }
    )

    try:
        dataframe["payload"].nunique(dropna=True)
    except TypeError:
        pass
    else:
        pytest.skip(
            "Phiên bản pandas hiện tại hỗ trợ value này trong nunique()."
        )

    with pytest.raises(InvalidDatasetError):
        detect_id_candidates(dataframe)


def test_detect_id_candidates_does_not_modify_dataframe(possible_id_dataframe) -> None:
    """Detector không thay đổi content, columns hoặc dtype nguồn."""

    before = possible_id_dataframe.copy(deep=True)
    before_columns = list(possible_id_dataframe.columns)
    before_dtypes = possible_id_dataframe.dtypes.copy()

    detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )

    pd.testing.assert_frame_equal(possible_id_dataframe, before)
    assert list(possible_id_dataframe.columns) == before_columns
    assert possible_id_dataframe.dtypes.equals(before_dtypes)


def test_detect_id_candidates_is_deterministic(possible_id_dataframe) -> None:
    """Cùng input và hints tạo ra kết quả giống nhau."""

    first = detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )
    second = detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )

    assert first == second


def test_detect_id_candidates_output_is_json_serializable(
    possible_id_dataframe,
) -> None:
    """Danh sách IdCandidateResult có thể serialize thành JSON."""

    result = detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )
    payload = [
        item.model_dump()
        for item in result
    ]
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    json.loads(serialized)


def test_detect_id_candidates_boolean_fields_are_booleans(
    possible_id_dataframe,
) -> None:
    """name_hint_match và candidate phải là bool thật."""

    result = detect_id_candidates(
        possible_id_dataframe,
        column_name_hints=["customer_id", "id"],
    )

    for item in result:
        assert isinstance(item.name_hint_match, bool)
        assert isinstance(item.candidate, bool)


def test_detect_id_candidates_rates_are_bounded(possible_id_dataframe) -> None:
    """Các rate được trả về đều nằm trong khoảng 0.0 đến 1.0."""

    result = detect_id_candidates(possible_id_dataframe)

    for item in result:
        if item.missing_rate is not None:
            assert 0.0 <= item.missing_rate <= 1.0
        if item.unique_rate is not None:
            assert 0.0 <= item.unique_rate <= 1.0
