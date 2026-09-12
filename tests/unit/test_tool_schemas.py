"""
W01-T02 — Schema contract tests

Kiểm tra các data contract trong src/tools/schemas.py.

Mục tiêu:
- Schema chấp nhận dữ liệu hợp lệ.
- Schema từ chối dữ liệu vi phạm contract.
- Rate luôn nằm trong khoảng 0.0 đến 1.0.
- Warning/error có cấu trúc rõ ràng.
- Các schema có thể serialize sang JSON.
"""

import json

import pytest
from pydantic import ValidationError

from src.tools import schemas


def test_dataset_reference_contains_load_metadata() -> None:
    """DatasetReference chỉ chứa metadata nhận diện dataset đã load."""

    reference = schemas.DatasetReference(
        path="data/sample.csv",
        format="csv",
        rows=100,
        columns=5,
    )

    assert reference.path == "data/sample.csv"
    assert reference.format == "csv"
    assert reference.rows == 100
    assert reference.columns == 5


def test_dataset_reference_rejects_negative_dimensions() -> None:
    """Rows và columns không được nhận giá trị âm."""

    with pytest.raises(ValidationError):
        schemas.DatasetReference.model_validate(
            {
                "path": "data/sample.csv",
                "format": "csv",
                "rows": -1,
                "columns": 5,
            }
        )

    with pytest.raises(ValidationError):
        schemas.DatasetReference.model_validate(
            {
                "path": "data/sample.csv",
                "format": "csv",
                "rows": 100,
                "columns": -1,
            }
        )


def test_dataset_reference_rejects_unsupported_format() -> None:
    """DatasetReference chỉ chấp nhận format đã được hỗ trợ."""

    with pytest.raises(ValidationError):
        schemas.DatasetReference.model_validate(
            {
                "path": "data/sample.pdf",
                "format": "pdf",
            }
        )


def test_rates_use_numeric_zero_to_one_convention() -> None:
    """Rate phải là số trong khoảng từ 0.0 đến 1.0."""

    result = schemas.MissingColumnResult(
        position=0,
        column="age",
        missing_count=5,
        missing_rate=0.5,
        severity="medium",
    )

    assert result.missing_rate == 0.5

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "position": 0,
                "column": "age",
                "missing_count": 5,
                "missing_rate": -0.1,
                "severity": "medium",
            }
        )

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "position": 0,
                "column": "age",
                "missing_count": 5,
                "missing_rate": 1.2,
                "severity": "medium",
            }
        )

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "position": 0,
                "column": "age",
                "missing_count": 5,
                "missing_rate": "35%",
                "severity": "medium",
            }
        )


def test_tool_warning_and_error_are_structured() -> None:
    """Warning và error phải có code, message và optional context."""

    warning = schemas.ToolWarning(
        code="DUPLICATE_COLUMN_NAME",
        message="Dataset contains duplicate column names.",
        context={"column": "customer_id"},
    )

    error = schemas.ToolError(
        code="FILE_NOT_FOUND",
        message="Dataset file could not be found.",
        context={"path": "data/sample.csv"},
    )

    assert warning.code == "DUPLICATE_COLUMN_NAME"
    assert warning.message == "Dataset contains duplicate column names."
    assert warning.context == {"column": "customer_id"}

    assert error.code == "FILE_NOT_FOUND"
    assert error.message == "Dataset file could not be found."
    assert error.context == {"path": "data/sample.csv"}


def test_tool_warning_and_error_allow_missing_context() -> None:
    """Context là optional và mặc định bằng None."""

    warning = schemas.ToolWarning(
        code="EMPTY_COLUMN_NAME",
        message="Dataset contains an empty column name.",
    )

    error = schemas.ToolError(
        code="INVALID_DATASET",
        message="Dataset is invalid.",
    )

    assert warning.context is None
    assert error.context is None


def test_tool_warning_and_error_reject_empty_code_or_message() -> None:
    """Code và message không được là chuỗi rỗng."""

    with pytest.raises(ValidationError):
        schemas.ToolWarning.model_validate(
            {
                "code": "",
                "message": "A warning occurred.",
            }
        )

    with pytest.raises(ValidationError):
        schemas.ToolError.model_validate(
            {
                "code": "FILE_NOT_FOUND",
                "message": "",
            }
        )


def test_missing_column_result_contains_count_rate_and_severity() -> None:
    """MissingColumnResult chứa đầy đủ count, rate và severity."""

    result = schemas.MissingColumnResult(
        position=0,
        column="income",
        missing_count=10,
        missing_rate=0.2,
        severity="medium",
    )

    assert result.column == "income"
    assert result.missing_count == 10
    assert result.missing_rate == 0.2
    assert result.severity == "medium"


def test_missing_column_result_rejects_negative_count() -> None:
    """Missing count không được âm."""

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "position": 0,
                "column": "income",
                "missing_count": -1,
                "missing_rate": 0.2,
                "severity": "medium",
            }
        )


def test_missing_column_result_rejects_unsupported_severity() -> None:
    """Severity ngoài policy tập trung không thuộc contract."""

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "position": 0,
                "column": "income",
                "missing_count": 1,
                "missing_rate": 0.1,
                "severity": "urgent",
            }
        )


def test_per_column_schemas_require_position() -> None:
    """Các contract theo cột phải định danh được cả cột trùng tên."""

    with pytest.raises(ValidationError):
        schemas.MissingColumnResult.model_validate(
            {
                "column": "income",
                "missing_count": 1,
                "missing_rate": 0.1,
                "severity": "medium",
            }
        )

    with pytest.raises(ValidationError):
        schemas.ColumnSummary.model_validate(
            {
                "column": "income",
                "dtype": "float64",
            }
        )


@pytest.mark.parametrize(
    "dtype_kind",
    [
        "numeric",
        "categorical",
        "datetime",
        "boolean",
        "unsupported",
    ],
)
def test_column_summary_accepts_supported_dtype_kinds(
    dtype_kind: schemas.DtypeKind,
) -> None:
    """ColumnSummary chấp nhận các dtype_kind đã quy ước."""

    summary = schemas.ColumnSummary(
        position=0,
        column="example_column",
        dtype="object",
        dtype_kind=dtype_kind,
        count=90,
        missing=10,
        missing_rate=0.1,
        unique=20,
    )

    assert summary.dtype_kind == dtype_kind


def test_column_summary_has_dtype_and_missing_convention() -> None:
    """ColumnSummary biểu diễn dtype và missing metadata rõ ràng."""

    summary = schemas.ColumnSummary(
        position=0,
        column="age",
        dtype="int64",
        dtype_kind="numeric",
        count=90,
        missing=10,
        missing_rate=0.1,
        unique=50,
    )

    assert summary.column == "age"
    assert summary.dtype == "int64"
    assert summary.dtype_kind == "numeric"
    assert summary.count == 90
    assert summary.missing == 10
    assert summary.missing_rate == 0.1
    assert summary.unique == 50


def test_column_summary_rejects_invalid_dtype_kind() -> None:
    """dtype_kind ngoài convention phải bị từ chối."""

    with pytest.raises(ValidationError):
        schemas.ColumnSummary.model_validate(
            {
                "position": 0,
                "column": "age",
                "dtype": "int64",
                "dtype_kind": "invalid_kind",
            }
        )


def test_column_summary_rejects_negative_counts() -> None:
    """Các field dạng count không được âm."""

    with pytest.raises(ValidationError):
        schemas.ColumnSummary.model_validate(
            {
                "position": 0,
                "column": "age",
                "dtype": "int64",
                "count": -1,
            }
        )

    with pytest.raises(ValidationError):
        schemas.ColumnSummary.model_validate(
            {
                "position": 0,
                "column": "age",
                "dtype": "int64",
                "missing": -1,
            }
        )

    with pytest.raises(ValidationError):
        schemas.ColumnSummary.model_validate(
            {
                "position": 0,
                "column": "age",
                "dtype": "int64",
                "unique": -1,
            }
        )

def test_dataset_load_result_contains_reference_and_warnings() -> None:
    """DatasetLoadResult chứa DatasetReference và danh sách warnings."""

    reference = schemas.DatasetReference(
        path="data/sample.csv",
        format="csv",
        rows=100,
        columns=5,
    )

    warning = schemas.ToolWarning(
        code="EMPTY_COLUMN_NAME",
        message="Dataset contains an empty column name.",
    )

    result = schemas.DatasetLoadResult(
        reference=reference,
        warnings=[warning],
    )

    assert result.reference == reference
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "EMPTY_COLUMN_NAME"

def test_schema_models_are_json_serializable() -> None:
    """Các common schema có thể serialize sang JSON."""

    warning = schemas.ToolWarning(
        code="DUPLICATE_COLUMN_NAME",
        message="Dataset contains duplicate column names.",
        context={"column": "customer_id"},
    )

    reference = schemas.DatasetReference(
        path="data/sample.csv",
        format="csv",
        rows=100,
        columns=5,
    )

    load_result = schemas.DatasetLoadResult(
        reference=reference,
        warnings=[warning],
    )

    error = schemas.ToolError(
        code="FILE_NOT_FOUND",
        message="Dataset file could not be found.",
        context={"path": "data/missing.csv"},
    )

    missing_result = schemas.MissingColumnResult(
        position=0,
        column="income",
        missing_count=10,
        missing_rate=0.2,
        severity="medium",
    )

    column_summary = schemas.ColumnSummary(
        position=0,
        column="income",
        dtype="float64",
        dtype_kind="numeric",
        count=90,
        missing=10,
        missing_rate=0.1,
        unique=80,
    )

    models = [
        warning,
        reference,
        load_result,
        error,
        missing_result,
        column_summary,
    ]

    for model in models:
        json_string = model.model_dump_json()

        assert isinstance(json_string, str)

        parsed = json.loads(json_string)

        assert isinstance(parsed, dict)
