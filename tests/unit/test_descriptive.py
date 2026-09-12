"""Kiểm thử behavior public của ``describe_numeric`` trong W01-T06."""

import json
import math

import pandas as pd
import pytest

from src.tools.descriptive import describe_categorical, describe_numeric
from src.tools.exceptions import InvalidConfigurationError, InvalidDatasetError


def test_describe_numeric_returns_expected_summary(
    numeric_descriptive_dataframe,
) -> None:
    """Numeric summary báo cáo đúng fact và giữ thứ tự cột nguồn."""

    result = describe_numeric(numeric_descriptive_dataframe)

    assert len(result) == 2
    assert [item.column for item in result] == ["score", "amount"]

    score = result[0]
    assert score.position == 0
    assert score.column == "score"
    assert isinstance(score.dtype, str)
    assert score.dtype
    assert score.count == 5
    assert score.missing_count == 0
    assert score.mean == pytest.approx(3.0)
    assert score.std == pytest.approx(1.5811388300841898)
    assert score.min == pytest.approx(1.0)
    assert score.q1 == pytest.approx(2.0)
    assert score.median == pytest.approx(3.0)
    assert score.q3 == pytest.approx(4.0)
    assert score.max == pytest.approx(5.0)

    amount = result[1]
    assert amount.position == 1
    assert amount.column == "amount"
    assert isinstance(amount.dtype, str)
    assert amount.dtype
    assert amount.count == 4
    assert amount.missing_count == 1
    assert amount.mean == pytest.approx(30.0)
    assert amount.std == pytest.approx(
        pd.Series([10.0, 20.0, 40.0, 50.0]).std()
    )
    assert amount.min == pytest.approx(10.0)
    assert amount.q1 == pytest.approx(17.5)
    assert amount.median == pytest.approx(30.0)
    assert amount.q3 == pytest.approx(42.5)
    assert amount.max == pytest.approx(50.0)


def test_describe_numeric_skips_boolean_columns() -> None:
    """Boolean dtype không được coi là numeric descriptive column."""

    dataframe = pd.DataFrame(
        {
            "value": [1, 2, 3],
            "flag": [True, False, True],
        }
    )

    result = describe_numeric(dataframe)

    assert [item.column for item in result] == ["value"]


def test_describe_numeric_skips_nullable_boolean() -> None:
    """Nullable boolean cũng phải được skip."""

    dataframe = pd.DataFrame(
        {
            "flag": pd.Series([True, False, None], dtype="boolean"),
        }
    )

    assert describe_numeric(dataframe) == []


def test_describe_numeric_skips_non_numeric_columns() -> None:
    """String/object không bị parse ngầm thành numeric."""

    dataframe = pd.DataFrame(
        {
            "city": ["HN", "HCM", "DN"],
            "numeric_text": ["1", "2", "3"],
        }
    )

    assert describe_numeric(dataframe) == []


def test_describe_numeric_skips_complex_dtype() -> None:
    """Complex dtype không thuộc numeric summary của tool này."""

    dataframe = pd.DataFrame(
        {
            "complex_value": pd.Series(
                [1 + 2j, 3 + 4j],
                dtype="complex128",
            )
        }
    )

    assert describe_numeric(dataframe) == []


def test_describe_numeric_handles_nullable_integer() -> None:
    """Nullable integer giữ count/missing và pandas statistics."""

    dataframe = pd.DataFrame(
        {
            "value": pd.Series([1, 2, None, 4], dtype="Int64"),
        }
    )

    result = describe_numeric(dataframe)
    item = result[0]
    series = dataframe["value"]

    assert item.count == 3
    assert item.missing_count == 1
    assert item.mean == pytest.approx(7 / 3)
    assert item.min == pytest.approx(1.0)
    assert item.median == pytest.approx(2.0)
    assert item.max == pytest.approx(4.0)
    assert item.q1 == pytest.approx(float(series.quantile(0.25)))
    assert item.q3 == pytest.approx(float(series.quantile(0.75)))


def test_describe_numeric_handles_nullable_float() -> None:
    """Nullable float được xử lý như numeric và bỏ qua missing value."""

    dataframe = pd.DataFrame(
        {
            "value": pd.Series([1.5, None, 3.5], dtype="Float64"),
        }
    )

    result = describe_numeric(dataframe)

    assert result[0].count == 2
    assert result[0].missing_count == 1
    assert result[0].mean == pytest.approx(2.5)


def test_describe_numeric_handles_all_null_numeric_column() -> None:
    """Cột numeric toàn null trả None cho toàn bộ statistic."""

    dataframe = pd.DataFrame(
        {
            "value": pd.Series([None, None, None], dtype="Float64"),
        }
    )

    result = describe_numeric(dataframe)
    item = result[0]

    assert item.count == 0
    assert item.missing_count == 3
    assert item.mean is None
    assert item.std is None
    assert item.min is None
    assert item.q1 is None
    assert item.median is None
    assert item.q3 is None
    assert item.max is None


def test_describe_numeric_handles_zero_rows_with_numeric_columns() -> None:
    """Numeric columns không có row vẫn có summary với statistic None."""

    dataframe = pd.DataFrame(
        {
            "value": pd.Series(dtype="float64"),
            "count": pd.Series(dtype="Int64"),
        }
    )

    result = describe_numeric(dataframe)

    assert len(result) == 2
    assert [(item.position, item.column) for item in result] == [
        (0, "value"),
        (1, "count"),
    ]

    for item in result:
        assert item.count == 0
        assert item.missing_count == 0
        assert item.mean is None
        assert item.std is None
        assert item.min is None
        assert item.q1 is None
        assert item.median is None
        assert item.q3 is None
        assert item.max is None


def test_describe_numeric_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả danh sách rỗng."""

    assert describe_numeric(pd.DataFrame()) == []


def test_describe_numeric_normalizes_single_value_std_to_none() -> None:
    """Một observed value có std NaN theo pandas nhưng output phải là None."""

    dataframe = pd.DataFrame(
        {
            "value": [100.0, None, None],
        }
    )

    item = describe_numeric(dataframe)[0]

    assert item.count == 1
    assert item.missing_count == 2
    assert item.mean == pytest.approx(100.0)
    assert item.min == pytest.approx(100.0)
    assert item.q1 == pytest.approx(100.0)
    assert item.median == pytest.approx(100.0)
    assert item.q3 == pytest.approx(100.0)
    assert item.max == pytest.approx(100.0)
    assert item.std is None


def test_describe_numeric_ignores_missing_values_in_statistics() -> None:
    """Missing value không được đưa vào descriptive statistics."""

    dataframe = pd.DataFrame(
        {
            "value": [1.0, None, 3.0, None, 5.0],
        }
    )

    item = describe_numeric(dataframe)[0]

    assert item.count == 3
    assert item.missing_count == 2
    assert item.mean == pytest.approx(3.0)
    assert item.median == pytest.approx(3.0)


def test_describe_numeric_preserves_duplicate_columns_by_position() -> None:
    """Duplicate labels vẫn được report theo physical position."""

    dataframe = pd.DataFrame(
        [
            [1, 10],
            [2, 20],
            [3, 30],
        ],
        columns=["value", "value"],
    )

    result = describe_numeric(dataframe)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "value"
    assert result[0].mean == pytest.approx(2.0)
    assert result[1].position == 1
    assert result[1].column == "value"
    assert result[1].mean == pytest.approx(20.0)


def test_describe_numeric_serializes_non_string_column_label() -> None:
    """Column label không phải string được chuyển thành string trong output."""

    dataframe = pd.DataFrame({123: [1, 2, 3]})

    item = describe_numeric(dataframe)[0]

    assert item.position == 0
    assert item.column == "123"


def test_describe_numeric_handles_empty_column_name() -> None:
    """Tên cột rỗng vẫn được giữ nguyên trong summary."""

    dataframe = pd.DataFrame(
        [[1], [2], [3]],
        columns=[""],
    )

    item = describe_numeric(dataframe)[0]

    assert item.column == ""
    assert item.mean == pytest.approx(2.0)


def test_describe_numeric_handles_multiple_numeric_dtypes() -> None:
    """Nhiều numeric dtype được report theo đúng thứ tự source."""

    dataframe = pd.DataFrame(
        {
            "int_col": pd.Series([1, 2], dtype="int64"),
            "float_col": pd.Series([1.5, 2.5], dtype="float64"),
            "nullable_int": pd.Series([1, None], dtype="Int64"),
            "nullable_float": pd.Series([1.5, None], dtype="Float64"),
        }
    )

    result = describe_numeric(dataframe)

    assert [item.column for item in result] == [
        "int_col",
        "float_col",
        "nullable_int",
        "nullable_float",
    ]
    assert len(result) == 4


def test_describe_numeric_skips_datetime_column() -> None:
    """Datetime không thuộc numeric descriptive summary."""

    dataframe = pd.DataFrame(
        {
            "event_time": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-02",
                ]
            )
        }
    )

    assert describe_numeric(dataframe) == []


@pytest.mark.parametrize(
    "invalid_input",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
    ids=["none", "list", "dict", "scalar"],
)
def test_describe_numeric_rejects_non_dataframe_input(invalid_input) -> None:
    """Input không phải DataFrame bị từ chối bằng lỗi typed."""

    with pytest.raises(InvalidDatasetError):
        describe_numeric(invalid_input)


def test_describe_numeric_does_not_modify_dataframe(
    numeric_descriptive_dataframe,
) -> None:
    """Tool không thay đổi content, columns hoặc dtype nguồn."""

    before = numeric_descriptive_dataframe.copy(deep=True)
    before_columns = list(numeric_descriptive_dataframe.columns)
    before_dtypes = numeric_descriptive_dataframe.dtypes.copy()

    describe_numeric(numeric_descriptive_dataframe)

    pd.testing.assert_frame_equal(numeric_descriptive_dataframe, before)
    assert list(numeric_descriptive_dataframe.columns) == before_columns
    assert numeric_descriptive_dataframe.dtypes.equals(before_dtypes)


def test_describe_numeric_is_deterministic(numeric_descriptive_dataframe) -> None:
    """Cùng input tạo ra cùng summary qua hai lần gọi."""

    first = describe_numeric(numeric_descriptive_dataframe)
    second = describe_numeric(numeric_descriptive_dataframe)

    assert first == second


def test_describe_numeric_output_is_json_serializable(
    numeric_descriptive_dataframe,
) -> None:
    """Output Pydantic v2 chuyển được sang JSON."""

    result = describe_numeric(numeric_descriptive_dataframe)
    payload = [item.model_dump() for item in result]

    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    assert isinstance(json.loads(serialized), list)


def test_describe_numeric_output_does_not_expose_non_finite_statistics() -> None:
    """NaN và infinity không được leak ra structured output."""

    dataframe = pd.DataFrame(
        {
            "value": [1.0, math.inf, -math.inf],
        }
    )

    result = describe_numeric(dataframe)

    for item in result:
        for value in [
            item.mean,
            item.std,
            item.min,
            item.q1,
            item.median,
            item.q3,
            item.max,
        ]:
            if value is not None:
                assert math.isfinite(value)


def _frequency_map(item):
    """Lập mapping value -> (count, rate) để tránh phụ thuộc tie-order."""

    return {
        frequency.value: (frequency.count, frequency.rate)
        for frequency in item.top_values
    }


def test_describe_categorical_returns_expected_summary(
    categorical_descriptive_dataframe,
) -> None:
    """Categorical summary báo cáo đúng supported dtype và frequency facts."""

    result = describe_categorical(categorical_descriptive_dataframe)

    assert len(result) == 3
    assert [item.column for item in result] == ["city", "segment", "active"]

    city = result[0]
    assert city.position == 0
    assert city.column == "city"
    assert isinstance(city.dtype, str)
    assert city.dtype
    assert city.count == 4
    assert city.missing_count == 1
    assert city.unique_count == 3
    city_top = _frequency_map(city)
    assert city_top["HN"] == (2, pytest.approx(0.5))
    assert city_top["HCM"] == (1, pytest.approx(0.25))
    assert city_top["DN"] == (1, pytest.approx(0.25))

    segment = result[1]
    assert segment.position == 1
    assert segment.column == "segment"
    assert segment.count == 5
    assert segment.missing_count == 0
    assert segment.unique_count == 2
    segment_top = _frequency_map(segment)
    assert segment_top["A"] == (3, pytest.approx(0.6))
    assert segment_top["B"] == (2, pytest.approx(0.4))

    active = result[2]
    assert active.position == 2
    assert active.column == "active"
    assert active.count == 4
    assert active.missing_count == 1
    assert active.unique_count == 2
    active_top = _frequency_map(active)
    assert active_top["True"] == (3, pytest.approx(0.75))
    assert active_top["False"] == (1, pytest.approx(0.25))


def test_describe_categorical_handles_object_dtype() -> None:
    """Object column được report là categorical."""

    dataframe = pd.DataFrame({"city": ["HN", "HN", "HCM"]})

    result = describe_categorical(dataframe)

    assert len(result) == 1
    assert result[0].column == "city"
    assert result[0].count == 3
    assert result[0].unique_count == 2


def test_describe_categorical_handles_string_dtype() -> None:
    """Pandas string extension dtype được report là categorical."""

    dataframe = pd.DataFrame(
        {
            "city": pd.Series(["HN", "HCM", None], dtype="string"),
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.count == 2
    assert item.missing_count == 1
    assert item.unique_count == 2


def test_describe_categorical_handles_boolean_dtype() -> None:
    """Boolean thường được report với value đã stringify."""

    dataframe = pd.DataFrame({"flag": [True, False, True]})

    item = describe_categorical(dataframe)[0]
    frequencies = _frequency_map(item)

    assert item.count == 3
    assert item.unique_count == 2
    assert frequencies["True"] == (2, pytest.approx(2 / 3))
    assert frequencies["False"] == (1, pytest.approx(1 / 3))


def test_describe_categorical_handles_nullable_boolean() -> None:
    """Nullable boolean được report và bỏ qua missing value."""

    dataframe = pd.DataFrame(
        {
            "flag": pd.Series([True, False, True, None], dtype="boolean"),
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.count == 3
    assert item.missing_count == 1
    assert item.unique_count == 2


def test_describe_categorical_handles_category_dtype() -> None:
    """Category dtype được report cùng các category đã quan sát."""

    dataframe = pd.DataFrame(
        {
            "segment": pd.Series(["A", "B", "A", None], dtype="category"),
        }
    )

    item = describe_categorical(dataframe)[0]
    frequencies = _frequency_map(item)

    assert item.count == 3
    assert item.missing_count == 1
    assert item.unique_count == 2
    assert frequencies["A"] == (2, pytest.approx(2 / 3))
    assert frequencies["B"] == (1, pytest.approx(1 / 3))


def test_describe_categorical_excludes_unobserved_categories() -> None:
    """Category khai báo nhưng chưa quan sát không xuất hiện trong output."""

    dtype = pd.CategoricalDtype(categories=["A", "B", "C"])
    dataframe = pd.DataFrame(
        {
            "segment": pd.Series(["A", "A", "B"], dtype=dtype),
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.unique_count == 2
    assert {frequency.value for frequency in item.top_values} == {"A", "B"}
    assert all(frequency.count > 0 for frequency in item.top_values)
    assert "C" not in {frequency.value for frequency in item.top_values}


def test_describe_categorical_keeps_numeric_looking_strings_as_categories() -> None:
    """String giống số vẫn giữ nguyên categorical semantics."""

    dataframe = pd.DataFrame({"code": ["1", "1", "2", "3"]})

    item = describe_categorical(dataframe)[0]
    frequencies = _frequency_map(item)

    assert item.unique_count == 3
    assert frequencies["1"] == (2, pytest.approx(0.5))


def test_describe_categorical_skips_numeric_columns() -> None:
    """Numeric và nullable numeric không được report categorical."""

    dataframe = pd.DataFrame(
        {
            "int_col": pd.Series([1, 2], dtype="int64"),
            "float_col": pd.Series([1.5, 2.5], dtype="float64"),
            "nullable_int": pd.Series([1, None], dtype="Int64"),
            "nullable_float": pd.Series([1.5, None], dtype="Float64"),
        }
    )

    assert describe_categorical(dataframe) == []


def test_describe_categorical_skips_complex_dtype() -> None:
    """Complex dtype không được report categorical."""

    dataframe = pd.DataFrame(
        {
            "complex_value": pd.Series([1 + 2j, 3 + 4j], dtype="complex128"),
        }
    )

    assert describe_categorical(dataframe) == []


def test_describe_categorical_skips_datetime_column() -> None:
    """Datetime không được report categorical."""

    dataframe = pd.DataFrame(
        {
            "event_time": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        }
    )

    assert describe_categorical(dataframe) == []


def test_describe_categorical_selects_only_supported_dtypes() -> None:
    """Supported categorical columns được giữ theo physical source order."""

    category_dtype = pd.CategoricalDtype(categories=["A", "B"])
    dataframe = pd.DataFrame(
        {
            "object_col": ["A", "B"],
            "string_col": pd.Series(["A", "B"], dtype="string"),
            "category_col": pd.Series(["A", "B"], dtype=category_dtype),
            "bool_col": [True, False],
            "nullable_bool": pd.Series([True, None], dtype="boolean"),
            "numeric_col": [1, 2],
            "datetime_col": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        }
    )

    result = describe_categorical(dataframe)

    assert [item.column for item in result] == [
        "object_col",
        "string_col",
        "category_col",
        "bool_col",
        "nullable_bool",
    ]
    assert [item.position for item in result] == [0, 1, 2, 3, 4]


def test_describe_categorical_excludes_missing_from_top_values() -> None:
    """None, NA và NaN không xuất hiện như category trong top_values."""

    dataframe = pd.DataFrame(
        {
            "city": [None, pd.NA, math.nan, "HN", "HN", "HCM"],
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.count == 3
    assert item.missing_count == 3
    assert item.unique_count == 2
    assert {frequency.value for frequency in item.top_values} == {"HN", "HCM"}
    assert all(frequency.value not in {"None", "<NA>", "nan"} for frequency in item.top_values)


def test_describe_categorical_handles_all_null_string_column() -> None:
    """Cột string toàn missing trả summary rỗng nhưng không raise."""

    dataframe = pd.DataFrame(
        {
            "value": pd.Series([None, None, None], dtype="string"),
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.count == 0
    assert item.missing_count == 3
    assert item.unique_count == 0
    assert item.top_values == []


def test_describe_categorical_handles_zero_rows_with_categorical_columns() -> None:
    """Categorical columns không có row vẫn được report với list rỗng."""

    dataframe = pd.DataFrame(
        {
            "city": pd.Series(dtype="string"),
            "flag": pd.Series(dtype="boolean"),
        }
    )

    result = describe_categorical(dataframe)

    assert len(result) == 2
    assert [(item.position, item.column) for item in result] == [
        (0, "city"),
        (1, "flag"),
    ]
    for item in result:
        assert item.count == 0
        assert item.missing_count == 0
        assert item.unique_count == 0
        assert item.top_values == []


def test_describe_categorical_handles_empty_dataframe() -> None:
    """DataFrame 0x0 trả danh sách rỗng."""

    assert describe_categorical(pd.DataFrame()) == []


def test_describe_categorical_respects_top_k() -> None:
    """top_k giới hạn top_values nhưng không giới hạn unique_count."""

    dataframe = pd.DataFrame(
        {
            "category": [
                "A",
                "A",
                "A",
                "A",
                "B",
                "B",
                "B",
                "C",
                "C",
                "D",
            ]
        }
    )

    item = describe_categorical(dataframe, top_k=2)[0]

    assert item.unique_count == 4
    assert len(item.top_values) == 2
    assert _frequency_map(item)["A"] == (4, pytest.approx(0.4))
    assert _frequency_map(item)["B"] == (3, pytest.approx(0.3))


def test_describe_categorical_allows_top_k_larger_than_unique_count() -> None:
    """top_k lớn hơn số category không tạo item padding."""

    dataframe = pd.DataFrame({"category": ["A", "A", "B"]})

    item = describe_categorical(dataframe, top_k=10)[0]

    assert item.unique_count == 2
    assert len(item.top_values) == 2


def test_describe_categorical_supports_top_k_one() -> None:
    """top_k=1 chỉ trả category có frequency cao nhất."""

    dataframe = pd.DataFrame({"category": ["A", "A", "B", "C"]})

    item = describe_categorical(dataframe, top_k=1)[0]

    assert len(item.top_values) == 1
    assert item.top_values[0].value == "A"
    assert item.top_values[0].count == 2


@pytest.mark.parametrize(
    "top_k",
    [0, -1, True, False, 1.5, "5", None],
    ids=["zero", "negative", "true", "false", "float", "string", "none"],
)
def test_describe_categorical_rejects_invalid_top_k(top_k) -> None:
    """top_k không phải positive int bị từ chối bằng typed error."""

    dataframe = pd.DataFrame({"category": ["A", "B"]})

    with pytest.raises(InvalidConfigurationError):
        describe_categorical(dataframe, top_k=top_k)


def test_describe_categorical_uses_default_top_k_five() -> None:
    """top_k mặc định bằng 5."""

    dataframe = pd.DataFrame(
        {
            "category": [
                *(["A"] * 7),
                *(["B"] * 6),
                *(["C"] * 5),
                *(["D"] * 4),
                *(["E"] * 3),
                *(["F"] * 2),
                "G",
            ]
        }
    )

    item = describe_categorical(dataframe)[0]

    assert item.unique_count == 7
    assert [frequency.value for frequency in item.top_values] == [
        "A",
        "B",
        "C",
        "D",
        "E",
    ]


def test_describe_categorical_rates_use_non_missing_denominator() -> None:
    """Rate dùng count non-missing làm denominator."""

    dataframe = pd.DataFrame({"category": ["A", "A", "B", None, None]})

    item = describe_categorical(dataframe)[0]
    frequencies = _frequency_map(item)

    assert item.count == 3
    assert item.missing_count == 2
    assert frequencies["A"] == (2, pytest.approx(2 / 3))
    assert frequencies["B"] == (1, pytest.approx(1 / 3))


def test_describe_categorical_rates_sum_to_one_when_all_categories_returned() -> None:
    """Khi top_k đủ lớn, tổng rate bằng 1.0."""

    dataframe = pd.DataFrame({"category": ["A", "A", "B", "C"]})

    item = describe_categorical(dataframe, top_k=10)[0]

    assert sum(frequency.rate for frequency in item.top_values) == pytest.approx(1.0)


def test_describe_categorical_preserves_duplicate_columns_by_position() -> None:
    """Duplicate labels vẫn được xử lý theo từng physical column."""

    dataframe = pd.DataFrame(
        [
            ["A", "X"],
            ["A", "Y"],
            ["B", "Y"],
        ],
        columns=["group", "group"],
    )

    result = describe_categorical(dataframe)

    assert len(result) == 2
    assert result[0].position == 0
    assert result[0].column == "group"
    assert result[0].unique_count == 2
    assert _frequency_map(result[0])["A"] == (2, pytest.approx(2 / 3))
    assert result[1].position == 1
    assert result[1].column == "group"
    assert result[1].unique_count == 2
    assert _frequency_map(result[1])["Y"] == (2, pytest.approx(2 / 3))


def test_describe_categorical_serializes_non_string_column_label() -> None:
    """Column label không phải string được stringify."""

    dataframe = pd.DataFrame({123: ["A", "A", "B"]})

    item = describe_categorical(dataframe)[0]

    assert item.position == 0
    assert item.column == "123"


def test_describe_categorical_handles_empty_column_name() -> None:
    """Tên cột rỗng vẫn được giữ nguyên."""

    dataframe = pd.DataFrame(
        [["A"], ["B"], ["A"]],
        columns=[""],
    )

    item = describe_categorical(dataframe)[0]

    assert item.column == ""
    assert item.count == 3
    assert item.unique_count == 2


def test_describe_categorical_serializes_category_values_as_strings() -> None:
    """CategoryFrequency.value luôn là string."""

    dataframe = pd.DataFrame({"flag": [True, False, True]})

    item = describe_categorical(dataframe)[0]

    assert {frequency.value for frequency in item.top_values} == {"True", "False"}
    assert all(isinstance(frequency.value, str) for frequency in item.top_values)


def test_describe_categorical_rejects_unhashable_object_values_when_frequency_cannot_be_computed(
) -> None:
    """Unhashable frequency chỉ raise khi pandas runtime không hỗ trợ chúng."""

    dataframe = pd.DataFrame(
        {
            "payload": [
                ["A"],
                ["B"],
                ["A"],
            ]
        }
    )

    try:
        pd.Series([["A"], ["B"], ["A"]]).value_counts()
    except TypeError:
        with pytest.raises(InvalidDatasetError):
            describe_categorical(dataframe)
    else:
        pytest.skip(
            "Current pandas runtime supports value_counts for this "
            "unhashable representative input."
        )


@pytest.mark.parametrize(
    "invalid_input",
    [None, [1, 2, 3], {"a": [1, 2]}, 42],
    ids=["none", "list", "dict", "scalar"],
)
def test_describe_categorical_rejects_non_dataframe_input(invalid_input) -> None:
    """Input không phải DataFrame bị từ chối bằng lỗi typed."""

    with pytest.raises(InvalidDatasetError):
        describe_categorical(invalid_input)


def test_describe_categorical_does_not_modify_dataframe(
    categorical_descriptive_dataframe,
) -> None:
    """Tool không thay đổi content, columns hoặc dtype nguồn."""

    before = categorical_descriptive_dataframe.copy(deep=True)
    before_columns = list(categorical_descriptive_dataframe.columns)
    before_dtypes = categorical_descriptive_dataframe.dtypes.copy()

    describe_categorical(categorical_descriptive_dataframe)

    pd.testing.assert_frame_equal(categorical_descriptive_dataframe, before)
    assert list(categorical_descriptive_dataframe.columns) == before_columns
    assert categorical_descriptive_dataframe.dtypes.equals(before_dtypes)


def test_describe_categorical_is_deterministic(categorical_descriptive_dataframe) -> None:
    """Cùng input tạo ra cùng categorical summary qua hai lần gọi."""

    first = describe_categorical(categorical_descriptive_dataframe)
    second = describe_categorical(categorical_descriptive_dataframe)

    assert first == second


def test_describe_categorical_output_is_json_serializable(
    categorical_descriptive_dataframe,
) -> None:
    """Output Pydantic v2 chuyển được sang JSON."""

    result = describe_categorical(categorical_descriptive_dataframe)
    payload = [item.model_dump() for item in result]

    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    assert isinstance(json.loads(serialized), list)


def test_describe_categorical_top_values_have_valid_frequency_contract(
    categorical_descriptive_dataframe,
) -> None:
    """Mỗi top frequency có value/count/rate hợp lệ."""

    result = describe_categorical(categorical_descriptive_dataframe)

    for item in result:
        for frequency in item.top_values:
            assert isinstance(frequency.value, str)
            assert frequency.count >= 1
            assert 0.0 <= frequency.rate <= 1.0


def test_describe_categorical_preserves_source_column_order() -> None:
    """Result positions giữ position vật lý, không đánh lại từ zero."""

    dataframe = pd.DataFrame(
        {
            "numeric_first": [1, 2],
            "category_a": ["A", "B"],
            "event_time": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "category_b": ["X", "Y"],
            "bool_col": [True, False],
            "numeric_last": [3, 4],
        }
    )

    result = describe_categorical(dataframe)

    assert [item.column for item in result] == [
        "category_a",
        "category_b",
        "bool_col",
    ]
    assert [item.position for item in result] == [1, 3, 4]
