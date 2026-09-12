"""
W01-T05 — Tool kiểm tra chất lượng dữ liệu

MỤC ĐÍCH
--------
Định nghĩa các phép kiểm tra deterministic, chỉ đọc cho missing value, duplicate,
cardinality, cột constant và ID candidate có khả năng.

KIẾN THỨC CẦN HỌC
------------------
1. Cách phân biệt phép đo với phần diễn giải.
2. Cách quy ước mẫu số và null làm thay đổi quality metric.
3. Vì sao duplicate detection nên báo cáo fact thay vì mutate dữ liệu.
4. Vì sao ID detector chỉ tìm candidate mà không thể chứng minh business meaning.
5. Cách configuration tập trung giữ policy severity nhất quán.

THỨ TỰ TRIỂN KHAI
------------------
1. Quyết định mẫu số theo dòng/cột và quy ước null.
2. Triển khai report đơn giản với schema tường minh.
3. Tách kiểm tra duplicate toàn dòng khỏi kiểm tra candidate key.
4. Định nghĩa quy ước all-null/constant trước khi code.
5. Coi ID detection là báo cáo evidence, không phải classification chắc chắn.
6. Thêm test bất biến, serialization và tính tất định cho từng tool.

RÀNG BUỘC QUAN TRỌNG
---------------------
- Không drop, fill, reorder hoặc mutate nguồn dữ liệu theo cách khác.
- Không rải threshold missing severity qua nhiều function.
- ``detect_id_candidates`` phải nói là candidate, không phải ID chắc chắn.
- Result phải có cấu trúc và dễ chuyển sang JSON.
"""

from __future__ import annotations

from typing import Any, Iterable, cast

import pandas as pd

from .config import (
    DEFAULT_MISSING_SEVERITY_CONFIG,
    MissingSeverity,
    MissingSeverityConfig,
    classify_missing_severity,
)
from .exceptions import (
    InvalidConfigurationError,
    InvalidDatasetError,
)
from .schemas import (
    CardinalityResult,
    ConstantColumnResult,
    DuplicateReport,
    IdCandidateResult,
    MissingColumnResult,
    MissingSeverityValue,
)


def _validate_dataframe(dataframe: Any) -> None:
    if not isinstance(dataframe, pd.DataFrame):
        raise InvalidDatasetError(
            "Expected a pandas DataFrame."
        )


def check_missing(
    dataframe: pd.DataFrame,
    *,
    config: MissingSeverityConfig | None = None,
) -> list[MissingColumnResult]:
    """Báo cáo missing count, rate và severity cho từng cột."""

    _validate_dataframe(dataframe)

    effective_config = (
        DEFAULT_MISSING_SEVERITY_CONFIG
        if config is None
        else config
    )

    classify_missing_severity(
        0.0,
        effective_config,
    )

    results: list[MissingColumnResult] = []

    total_rows = len(dataframe)

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        missing_count = int(series.isna().sum())

        if total_rows == 0:
            missing_rate = None
        else:
            missing_rate = float(
                missing_count / total_rows
            )

        if missing_rate is None:
            severity = cast(MissingSeverityValue, MissingSeverity.NONE.value)
        else:
            severity = cast(
                MissingSeverityValue,
                classify_missing_severity(
                    missing_rate,
                    effective_config,
                ).value,
            )

        results.append(
            MissingColumnResult(
                position=position,
                column=str(column),
                missing_count=missing_count,
                missing_rate=missing_rate,
                severity=severity,
            )
        )

    return results


def check_duplicates(
    dataframe: pd.DataFrame,
    *,
    candidate_key: str | Iterable[str] | None = None,
) -> DuplicateReport:
    """Báo cáo duplicate toàn dòng và duplicate theo candidate key.

    Quy ước:
    - Duplicate count chỉ tính các occurrence xuất hiện sau occurrence đầu tiên.
    - Duplicate rate = duplicate_count / total_rows.
    - Với zero rows, duplicate rate = None.
    - candidate_key=None nghĩa là không thực hiện kiểm tra duplicate theo key.
    - candidate_key chỉ nhận nhãn cột dạng chuỗi; đây là API chủ đích của Week 01.
    - Null trong candidate key tuân theo semantics của pandas ``duplicated``.
    - Giá trị không hashable làm phép đo thất bại với ``InvalidDatasetError``.
    - Function chỉ báo cáo evidence, không xóa hoặc thay đổi dữ liệu.
    """

    # 1. Validate DataFrame

    _validate_dataframe(dataframe)

    total_rows = len(dataframe)

    # 2. Full-row duplicate evidence

    try:
        full_row_duplicate_count = int(
            dataframe.duplicated().sum()
        )
    except TypeError as exc:
        raise InvalidDatasetError(
            "Cannot check full-row duplicates because the DataFrame "
            "contains values that are not hashable."
        ) from exc

    if total_rows == 0:
        full_row_duplicate_rate = None
    else:
        full_row_duplicate_rate = float(
            full_row_duplicate_count / total_rows
        )

    # 3. No candidate key requested

    if candidate_key is None:
        key_columns = None
        candidate_key_duplicate_count = None
        candidate_key_duplicate_rate = None

    # 4. Normalize and validate candidate key

    else:
        if isinstance(candidate_key, str):
            key_columns = [candidate_key]

        else:
            try:
                key_columns = list(candidate_key)
            except TypeError as exc:
                raise InvalidConfigurationError(
                    "candidate_key must be a column name or an iterable "
                    "of column names."
                ) from exc

        # Empty key collection is invalid.
        if not key_columns:
            raise InvalidConfigurationError(
                "candidate_key must contain at least one column."
            )

        # Candidate-key labels must be strings.
        if any(
            not isinstance(column, str)
            for column in key_columns
        ):
            raise InvalidConfigurationError(
                "candidate_key columns must be strings."
            )

        # Empty string is not accepted as a candidate-key name.
        if any(column == "" for column in key_columns):
            raise InvalidConfigurationError(
                "candidate_key columns must not be empty strings."
            )

        # The same key column must not be supplied more than once.
        if len(set(key_columns)) != len(key_columns):
            raise InvalidConfigurationError(
                "candidate_key must not contain duplicate column names."
            )

        # 5. Validate candidate-key columns against DataFrame

        dataframe_columns = list(dataframe.columns)

        for key in key_columns:
            matches = dataframe_columns.count(key)

            if matches == 0:
                raise InvalidConfigurationError(
                    f"Candidate key column '{key}' does not exist."
                )

            if matches > 1:
                raise InvalidConfigurationError(
                    f"Candidate key column '{key}' is ambiguous because "
                    "the DataFrame contains duplicate column labels."
                )

        # 6. Candidate-key duplicate evidence

        try:
            candidate_key_duplicate_count = int(
                dataframe.duplicated(
                    subset=key_columns
                ).sum()
            )
        except TypeError as exc:
            raise InvalidDatasetError(
                "Cannot check candidate-key duplicates because the "
                "selected columns contain values that are not hashable."
            ) from exc

        if total_rows == 0:
            candidate_key_duplicate_rate = None
        else:
            candidate_key_duplicate_rate = float(
                candidate_key_duplicate_count / total_rows
            )

    # 7. Structured result

    return DuplicateReport(
        total_rows=total_rows,
        full_row_duplicate_count=full_row_duplicate_count,
        full_row_duplicate_rate=full_row_duplicate_rate,
        candidate_key=key_columns,
        candidate_key_duplicate_count=candidate_key_duplicate_count,
        candidate_key_duplicate_rate=candidate_key_duplicate_rate,
    )


def check_cardinality(
    dataframe: pd.DataFrame,
) -> list[CardinalityResult]:
    """Báo cáo cardinality theo từng cột.

    Quy ước:
    - Missing value không được tính là một unique value.
    - unique_count = số giá trị distinct non-missing.
    - unique_rate = unique_count / non_missing_count.
    - unique_rate = None khi không có giá trị non-missing.
    - Giá trị không hashable làm phép đo thất bại với ``InvalidDatasetError``.
    - Function không mutate DataFrame.
    """

    _validate_dataframe(dataframe)

    results: list[CardinalityResult] = []

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        non_missing_count = int(
            series.notna().sum()
        )

        try:
            unique_count = int(
                series.nunique(dropna=True)
            )
        except TypeError as exc:
            raise InvalidDatasetError(
                f"Cannot calculate cardinality for column "
                f"at position {position} because it contains "
                "values that are not hashable."
            ) from exc

        if non_missing_count == 0:
            unique_rate = None
        else:
            unique_rate = float(
                unique_count / non_missing_count
            )

        results.append(
            CardinalityResult(
                position=position,
                column=str(column),
                non_missing_count=non_missing_count,
                unique_count=unique_count,
                unique_rate=unique_rate,
            )
        )

    return results


def check_constant_columns(
    dataframe: pd.DataFrame,
) -> list[ConstantColumnResult]:
    """Báo cáo evidence về các cột constant.

    Quy ước:
    - Missing value không được tính là distinct value.
    - Cột constant khi có ít nhất một non-missing value và chỉ có
      đúng một distinct non-missing value.
    - Cột all-null không được coi là constant.
    - Zero-row column không được coi là all-null hay constant.
    - Giá trị không hashable làm phép đo thất bại với ``InvalidDatasetError``.
    - Function không mutate DataFrame.
    """

    _validate_dataframe(dataframe)

    total_rows = len(dataframe)

    results: list[ConstantColumnResult] = []

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        series = dataframe.iloc[:, position]

        non_missing_count = int(
            series.notna().sum()
        )

        try:
            unique_count = int(
                series.nunique(dropna=True)
            )
        except TypeError as exc:
            raise InvalidDatasetError(
                f"Cannot check whether column at position {position} "
                "is constant because it contains values that are not hashable."
            ) from exc

        is_all_null = (
            total_rows > 0
            and non_missing_count == 0
        )

        is_constant = (
            non_missing_count > 0
            and unique_count == 1
        )

        results.append(
            ConstantColumnResult(
                position=position,
                column=str(column),
                total_rows=total_rows,
                non_missing_count=non_missing_count,
                unique_count=unique_count,
                is_all_null=is_all_null,
                is_constant=is_constant,
            )
        )

    return results


def detect_id_candidates(
    dataframe: pd.DataFrame,
    *,
    column_name_hints: Iterable[str] | None = None,
) -> list[IdCandidateResult]:
    """Báo cáo evidence cho các cột có khả năng là ID candidate.

    Quy ước:
    - Missing không tính là unique value.
    - Name hint chỉ là evidence yếu và không quyết định candidate.
    - Một cột là candidate khi:
        * DataFrame có ít nhất 2 rows;
        * không có missing;
        * mọi row có một giá trị unique.
    - Candidate không đồng nghĩa với business identifier chắc chắn.
    - Giá trị không hashable làm phép đo thất bại với ``InvalidDatasetError``.
    - Function không mutate DataFrame.
    """

    _validate_dataframe(dataframe)

    # ============================================================
    # 1. Normalize column-name hints
    # ============================================================

    if column_name_hints is None:
        normalized_hints: set[str] = set()

    elif isinstance(column_name_hints, str):
        if column_name_hints == "":
            raise InvalidConfigurationError(
                "column_name_hints must not contain empty strings."
            )

        normalized_hints = {
            column_name_hints.casefold()
        }

    else:
        try:
            hints = list(column_name_hints)
        except TypeError as exc:
            raise InvalidConfigurationError(
                "column_name_hints must be a string or an iterable of strings."
            ) from exc

        if any(
            not isinstance(hint, str)
            for hint in hints
        ):
            raise InvalidConfigurationError(
                "column_name_hints must contain only strings."
            )

        if any(hint == "" for hint in hints):
            raise InvalidConfigurationError(
                "column_name_hints must not contain empty strings."
            )

        normalized_hints = {
            hint.casefold()
            for hint in hints
        }

    # ============================================================
    # 2. Gather evidence
    # ============================================================

    total_rows = len(dataframe)

    results: list[IdCandidateResult] = []

    for position in range(dataframe.shape[1]):
        column = dataframe.columns[position]
        column_name = str(column)
        series = dataframe.iloc[:, position]

        non_missing_count = int(
            series.notna().sum()
        )

        missing_count = int(
            series.isna().sum()
        )

        if total_rows == 0:
            missing_rate = None
        else:
            missing_rate = float(
                missing_count / total_rows
            )

        try:
            unique_count = int(
                series.nunique(dropna=True)
            )
        except TypeError as exc:
            raise InvalidDatasetError(
                f"Cannot evaluate ID candidacy for column "
                f"at position {position} because it contains "
                "values that are not hashable."
            ) from exc

        if non_missing_count == 0:
            unique_rate = None
        else:
            unique_rate = float(
                unique_count / non_missing_count
            )

        dtype = str(series.dtype)

        name_hint_match = (
            column_name.casefold()
            in normalized_hints
        )

        candidate = (
            total_rows >= 2
            and missing_count == 0
            and unique_count == total_rows
        )

        results.append(
            IdCandidateResult(
                position=position,
                column=column_name,
                dtype=dtype,
                total_rows=total_rows,
                non_missing_count=non_missing_count,
                missing_count=missing_count,
                missing_rate=missing_rate,
                unique_count=unique_count,
                unique_rate=unique_rate,
                name_hint_match=name_hint_match,
                candidate=candidate,
            )
        )

    return results
