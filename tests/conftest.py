"""
W01-T07 — Skeleton fixture

MỤC ĐÍCH
--------
Chuẩn bị các fixture nhỏ, có tên rõ ràng cho ma trận behavior của Week 01.
Fixture cố ý để trống để người học tự quyết định dữ liệu nào minh họa tốt nhất
cho từng khái niệm, thay vì kế thừa các giả định implementation bị ẩn.

THỨ TỰ TRIỂN KHAI
------------------
1. Bắt đầu với một DataFrame bình thường, nhỏ.
2. Tạo một fixture tập trung cho từng trường hợp biên.
3. Chỉ thêm fixture file tạm cho test loader.
4. Giữ fixture deterministic, local, nhỏ và không chứa dữ liệu nhạy cảm.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def normal_dataframe() -> pd.DataFrame:
    """DataFrame nhỏ, deterministic cho các kiểm thử quality/descriptive."""

    return pd.DataFrame(
        {
            "customer_id": list(range(1, 11)),
            "age": [
                20,
                21,
                None,
                23,
                24,
                None,
                26,
                27,
                28,
                29,
            ],
            "city": [
                "HN",
                "HN",
                "HCM",
                "HCM",
                "HN",
                "DN",
                "HN",
                None,
                "HCM",
                "HN",
            ],
            "income": [
                100,
                200,
                300,
                None,
                500,
                None,
                700,
                800,
                None,
                1000,
            ],
        }
    )


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """DataFrame có schema rõ ràng nhưng không có observation."""

    return pd.DataFrame(
        {
            "customer_id": pd.Series(dtype="int64"),
            "age": pd.Series(dtype="float64"),
            "city": pd.Series(dtype="string"),
            "active": pd.Series(dtype="boolean"),
        }
    )



@pytest.fixture
def all_null_column_dataframe() -> pd.DataFrame:
    """DataFrame có một cột toàn null và một cột có dữ liệu."""

    return pd.DataFrame(
        {
            "all_null": [
                None,
                None,
                None,
            ],
            "id": [
                1,
                2,
                3,
            ],
        }
    )


@pytest.fixture
def duplicate_rows_dataframe() -> pd.DataFrame:
    """DataFrame có duplicate toàn dòng và duplicate theo candidate key."""

    return pd.DataFrame(
        {
            "customer_id": [1, 2, 1, 2, 3],
            "city": [
                "HN",
                "HCM",
                "HN",
                "DN",
                "HUE",
            ],
            "amount": [
                100,
                200,
                100,
                300,
                400,
            ],
        }
    )


@pytest.fixture
def mixed_dtype_dataframe() -> pd.DataFrame:
    """DataFrame chứa nhiều dtype đại diện cho các tool Week 01."""

    event_time = pd.Series(
        pd.to_datetime(
            [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-04",
            ]
        )
    )

    event_time.iloc[2] = None

    return pd.DataFrame(
        {
            "score": pd.Series(
                [10, 20, 30, 40],
                dtype="int64",
            ),
            "city": pd.Series(
                ["HN", "HCM", "DN", None],
                dtype="string",
            ),
            "event_time": event_time,
            "active": pd.Series(
                [True, False, True, None],
                dtype="boolean",
            ),
            "mixed_value": pd.Series(
                [1, "two", 3.5, None],
                dtype="object",
            ),
        }
    )



@pytest.fixture
def constant_column_dataframe() -> pd.DataFrame:
    """DataFrame có cột constant rõ ràng và cột non-constant."""

    return pd.DataFrame(
        {
            "segment": [
                "A",
                "A",
                "A",
                "A",
            ],
            "city": [
                "HN",
                "HCM",
                "DN",
                "HN",
            ],
        }
    )


@pytest.fixture
def high_cardinality_string_dataframe() -> pd.DataFrame:
    """DataFrame nhỏ có cột string với cardinality cao."""

    return pd.DataFrame(
        {
            "customer_code": [
                "C001",
                "C002",
                "C003",
                "C004",
                "C005",
                "C006",
                "C007",
                "C008",
                "C009",
                "C010",
            ],
            "city": [
                "HN",
                "HN",
                "HCM",
                "HN",
                "HCM",
                "DN",
                "HN",
                "HCM",
                "DN",
                "HN",
            ],
            "segment": [
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
                "A",
            ],
        }
    )


@pytest.fixture
def possible_id_dataframe() -> pd.DataFrame:
    """DataFrame chứa ID candidate và các cột đối chứng."""

    return pd.DataFrame(
        {
            "customer_id": [
                "C001",
                "C002",
                "C003",
                "C004",
                "C005",
            ],
            "city": [
                "HN",
                "HN",
                "HCM",
                "DN",
                "HN",
            ],
            "reference_code": [
                "R01",
                "R02",
                None,
                "R04",
                "R05",
            ],
            "id": [
                1,
                1,
                1,
                1,
                1,
            ],
        }
    )


@pytest.fixture
def numeric_descriptive_dataframe() -> pd.DataFrame:
    """DataFrame nhỏ để kiểm thử descriptive statistics cho numeric columns."""

    return pd.DataFrame(
        {
            "score": [
                1,
                2,
                3,
                4,
                5,
            ],
            "amount": [
                10.0,
                20.0,
                None,
                40.0,
                50.0,
            ],
            "active": [
                True,
                False,
                True,
                False,
                True,
            ],
            "city": [
                "HN",
                "HCM",
                "HN",
                "DN",
                "HCM",
            ],
        }
    )


@pytest.fixture
def invalid_path(tmp_path: Path) -> Path:
    """Đường dẫn chắc chắn không tồn tại."""

    path = tmp_path / "missing_dataset.csv"

    assert not path.exists()

    return path


@pytest.fixture
def unsupported_format_path(tmp_path: Path) -> Path:
    """File tồn tại nhưng có extension không được loader hỗ trợ."""

    path = tmp_path / "dataset.unsupported"

    path.write_text(
        "dummy content",
        encoding="utf-8",
    )

    return path


@pytest.fixture
def categorical_descriptive_dataframe() -> pd.DataFrame:
    """DataFrame nhỏ để kiểm thử categorical descriptive statistics."""

    return pd.DataFrame(
        {
            "city": [
                "HN",
                "HN",
                "HCM",
                "DN",
                None,
            ],
            "segment": [
                "A",
                "A",
                "B",
                "A",
                "B",
            ],
            "active": pd.Series(
                [True, False, True, True, None],
                dtype="boolean",
            ),
            "score": [
                1,
                2,
                3,
                4,
                5,
            ],
        }
    )