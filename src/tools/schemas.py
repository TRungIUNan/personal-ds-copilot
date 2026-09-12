from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DtypeKind = Literal[
    "numeric",
    "categorical",
    "datetime",
    "boolean",
    "unsupported",
]

MissingSeverityValue = Literal[
    "none",
    "low",
    "medium",
    "high",
    "critical",
]


class ToolWarning(BaseModel):
    """Cảnh báo có cấu trúc, không làm tool thất bại."""

    code: str = Field(
        ...,
        min_length=1,
        description="Mã cảnh báo ổn định dùng để phân loại warning.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Thông báo cảnh báo an toàn và dễ hiểu.",
    )

    context: dict[str, Any] | None = Field(
        default=None,
        description="Thông tin bổ sung an toàn liên quan đến warning.",
    )


class DatasetReference(BaseModel):
    """Metadata ổn định dùng để nhận diện một dataset đã load."""

    path: str = Field(..., min_length=1, description="Đường dẫn tới dataset.")
    format: Literal["csv", "excel", "parquet"]
    rows: int | None = Field(
        default=None,
        ge=0,
        description="Số lượng dòng, nếu đã biết; không được âm.",
    )
    columns: int | None = Field(
        default=None,
        ge=0,
        description="Số lượng cột, nếu đã biết; không được âm.",
    )


class ToolError(BaseModel):
    """Mô tả có cấu trúc cho một lỗi dự kiến của tool."""

    code: str = Field(
        ...,
        min_length=1,
        description="Mã lỗi ổn định dùng để phân loại lỗi.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Thông báo lỗi an toàn và dễ hiểu.",
    )

    context: dict[str, Any] | None = Field(
        default=None,
        description="Thông tin bổ sung an toàn liên quan đến lỗi.",
    )


class ColumnSummary(BaseModel):
    """Contract cho summary ngắn gọn của một cột DataFrame."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột trong DataFrame.",
    )

    column: str = Field(
        ...,
        description="Tên gốc của cột trong DataFrame.",
    )
    dtype: str = Field(
        ...,
        min_length=1,
        description="Dtype gốc của cột.",
    )
    dtype_kind: DtypeKind | None = None
    count: int | None = Field(
        default=None,
        ge=0,
        description="Số giá trị non-missing.",
    )
    missing: int | None = Field(
        default=None,
        ge=0,
        description="Số giá trị missing.",
    )
    missing_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Tỉ lệ missing.",
    )
    unique: int | None = Field(
        default=None,
        ge=0,
        description="Số giá trị unique.",
    )


class MissingColumnResult(BaseModel):
    """Contract cho thông tin missing value của một cột."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột trong DataFrame.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột trong DataFrame.",
    )

    missing_count: int = Field(
        ...,
        ge=0,
        description="Số lượng giá trị missing của cột, không được âm.",
    )

    missing_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Tỷ lệ missing trong khoảng 0.0–1.0; "
            "None khi DataFrame có zero rows."
        ),
    )

    severity: MissingSeverityValue


class DatasetLoadResult(BaseModel):
    """Metadata envelope cho kết quả load dataset."""

    reference: DatasetReference

    warnings: list[ToolWarning] = Field(default_factory=list)


class ShapeResult(BaseModel):
    """Structured result mô tả kích thước của DataFrame."""

    rows: int = Field(
        ...,
        ge=0,
        description="Số lượng dòng của DataFrame, không được âm.",
    )

    columns: int = Field(
        ...,
        ge=0,
        description="Số lượng cột của DataFrame, không được âm.",
    )


class ColumnDtype(BaseModel):
    """Thông tin dtype của một cột trong DataFrame."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột trong DataFrame.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    dtype: str = Field(
        ...,
        min_length=1,
        description="Tên dtype gốc do pandas báo cáo.",
    )

    dtype_kind: DtypeKind


class DtypeResult(BaseModel):
    """Structured result chứa dtype của các cột."""

    columns: list[ColumnDtype] = Field(
        default_factory=list,
        description="Danh sách thông tin dtype của các cột theo thứ tự trong DataFrame.",
    )


class SchemaResult(BaseModel):
    """Structured result mô tả schema của DataFrame."""

    columns: list[ColumnDtype] = Field(
        default_factory=list,
        description="Danh sách cột và dtype theo đúng thứ tự nguồn.",
    )

    warnings: list[ToolWarning] = Field(
        default_factory=list,
        description="Các cảnh báo cấu trúc liên quan đến tên cột.",
    )


class PreviewResult(BaseModel):
    """Structured preview có giới hạn của DataFrame."""

    columns: list[str] = Field(
        default_factory=list,
        description="Tên các cột được trả về theo đúng thứ tự nguồn.",
    )

    rows: list[list[Any]] = Field(
        default_factory=list,
        description="Các dòng preview tương ứng với thứ tự trong columns.",
    )

    total_rows: int = Field(
        ...,
        ge=0,
        description="Tổng số dòng của DataFrame nguồn.",
    )

    total_columns: int = Field(
        ...,
        ge=0,
        description="Tổng số cột của DataFrame nguồn.",
    )

    returned_rows: int = Field(
        ...,
        ge=0,
        description="Số dòng thực tế được trả về.",
    )

    returned_columns: int = Field(
        ...,
        ge=0,
        description="Số cột thực tế được trả về.",
    )

    rows_truncated: bool

    columns_truncated: bool


class DuplicateReport(BaseModel):
    """Evidence về duplicate toàn dòng và theo candidate key."""

    total_rows: int = Field(
        ...,
        ge=0,
        description="Tổng số dòng trong DataFrame.",
    )

    full_row_duplicate_count: int = Field(
        ...,
        ge=0,
        description="Số occurrence duplicate toàn dòng sau occurrence đầu tiên.",
    )

    full_row_duplicate_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Tỷ lệ duplicate toàn dòng; "
            "None khi DataFrame có zero rows."
        ),
    )

    candidate_key: list[str] | None = None

    candidate_key_duplicate_count: int | None = Field(
        default=None,
        ge=0,
    )

    candidate_key_duplicate_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class CardinalityResult(BaseModel):
    """Evidence cardinality của một cột."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    non_missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị non-missing được quan sát.",
    )

    unique_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị distinct không tính missing.",
    )

    unique_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "unique_count / non_missing_count; "
            "None khi không có giá trị non-missing."
        ),
    )


class ConstantColumnResult(BaseModel):
    """Evidence cho việc một cột có phải constant hay không."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    total_rows: int = Field(
        ...,
        ge=0,
        description="Tổng số dòng của DataFrame nguồn.",
    )

    non_missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị non-missing được quan sát.",
    )

    unique_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị distinct non-missing.",
    )

    is_all_null: bool = Field(
        ...,
        description=(
            "True khi DataFrame có ít nhất một dòng "
            "nhưng cột không có giá trị non-missing."
        ),
    )

    is_constant: bool = Field(
        ...,
        description=(
            "True khi có ít nhất một giá trị non-missing "
            "và chỉ có đúng một giá trị distinct."
        ),
    )


class IdCandidateResult(BaseModel):
    """Evidence cho một cột có khả năng là identifier candidate."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    dtype: str = Field(
        ...,
        min_length=1,
        description="Dtype gốc do pandas báo cáo.",
    )

    total_rows: int = Field(
        ...,
        ge=0,
        description="Tổng số dòng của DataFrame.",
    )

    non_missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị non-missing.",
    )

    missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị missing.",
    )

    missing_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Tỷ lệ missing; None khi DataFrame có zero rows."
        ),
    )

    unique_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị distinct non-missing.",
    )

    unique_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "unique_count / non_missing_count; "
            "None khi không có giá trị non-missing."
        ),
    )

    name_hint_match: bool = Field(
        ...,
        description=(
            "Tên cột có match một caller-provided hint hay không. "
            "Đây chỉ là evidence yếu."
        ),
    )

    candidate: bool = Field(
        ...,
        description=(
            "True khi cột thỏa heuristic candidate đã document; "
            "không khẳng định business identity."
        ),
    )

class NumericSummaryResult(BaseModel):
    """Thống kê mô tả cho một cột numeric."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    dtype: str = Field(
        ...,
        min_length=1,
        description="Dtype gốc do pandas báo cáo.",
    )

    count: int = Field(
        ...,
        ge=0,
        description="Số giá trị non-missing.",
    )

    missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị missing.",
    )

    mean: float | None = None
    std: float | None = None
    min: float | None = None
    q1: float | None = None
    median: float | None = None
    q3: float | None = None
    max: float | None = None

class CategoryFrequency(BaseModel):
    """Frequency evidence cho một categorical value."""

    value: str = Field(
        ...,
        description="String representation của category.",
    )

    count: int = Field(
        ...,
        ge=0,
        description="Số lần category xuất hiện.",
    )

    rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Tỷ lệ category trên tổng số non-missing values.",
    )

class CategoricalSummaryResult(BaseModel):
    """Thống kê mô tả cho một categorical column."""

    position: int = Field(
        ...,
        ge=0,
        description="Vị trí zero-based của cột.",
    )

    column: str = Field(
        ...,
        description="Biểu diễn tên cột.",
    )

    dtype: str = Field(
        ...,
        min_length=1,
        description="Dtype gốc do pandas báo cáo.",
    )

    count: int = Field(
        ...,
        ge=0,
        description="Số giá trị non-missing.",
    )

    missing_count: int = Field(
        ...,
        ge=0,
        description="Số giá trị missing.",
    )

    unique_count: int = Field(
        ...,
        ge=0,
        description="Số distinct non-missing values.",
    )

    top_values: list[CategoryFrequency] = Field(
        default_factory=list,
        description="Các category phổ biến nhất theo frequency.",
    )