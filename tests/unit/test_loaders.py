"""
W01-T03 — Kiểm thử behavior của các loader

MỤC ĐÍCH
--------
Kiểm tra behavior thực tế của ``load_csv``, ``load_excel`` và ``load_parquet``
qua các file nhỏ được tạo trong ``tmp_path`` của pytest.

RÀNG BUỘC
---------
- Không dùng internet hay dataset cố định trong repository.
- Mỗi test tập trung vào một behavior có tên rõ ràng.
- Hash file chỉ dùng để kiểm tra source file không bị thay đổi.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from src.tools.exceptions import (
    DatasetParsingError,
    FileNotFoundToolError,
    InvalidConfigurationError,
    InvalidDatasetError,
    UnsupportedFormatError,
)
from src.tools.loaders import load_csv, load_dataset, load_excel, load_parquet


def _sample_dataframe() -> pd.DataFrame:
    """Tạo DataFrame nhỏ, deterministic dùng chung cho các test loader."""

    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Carol"],
            "value": [10.5, 20.0, 30.25],
        }
    )


def _file_sha256(path: Path) -> str:
    """Tính SHA-256 theo chunk để so sánh bytes trước và sau khi load."""

    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_empty_warnings(result) -> None:
    """Kiểm tra warnings mặc định rỗng ở result envelope."""

    assert result.warnings == []


def _assert_metadata(
    result,
    *,
    path: Path,
    file_format: str,
    rows: int,
    columns: int,
) -> None:
    """Kiểm tra metadata chung của DatasetLoadResult."""

    assert result.reference.path == str(path)
    assert result.reference.format == file_format
    assert result.reference.rows == rows
    assert result.reference.columns == columns
    _assert_empty_warnings(result)


def _assert_result_is_json_serializable(result) -> None:
    """Kiểm tra DatasetLoadResult có thể chuyển thành JSON bằng Pydantic v2."""

    payload = result.model_dump_json()

    assert isinstance(payload, str)
    json.loads(payload)


def _write_excel_workbook(path: Path) -> None:
    """Tạo workbook hai sheet nhỏ để test behavior chọn sheet."""

    first = _sample_dataframe()
    second = pd.DataFrame(
        {
            "id": [10, 20],
            "name": ["Delta", "Echo"],
            "value": [100.5, 225.25],
        }
    )

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        first.to_excel(writer, sheet_name="SheetA", index=False)
        second.to_excel(writer, sheet_name="SheetB", index=False)


def test_load_csv_returns_dataframe_and_metadata(tmp_path: Path) -> None:
    """CSV hợp lệ trả DataFrame đúng và metadata đầy đủ."""

    path = tmp_path / "sample.csv"
    expected = _sample_dataframe()
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_csv(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="csv",
        rows=3,
        columns=3,
    )
    _assert_result_is_json_serializable(result)


def test_load_csv_raises_for_missing_file(invalid_path: Path) -> None:
    """CSV loader raise FileNotFoundToolError khi file không tồn tại."""

    with pytest.raises(FileNotFoundToolError):
        load_csv(invalid_path)


def test_load_csv_rejects_directory_path(tmp_path: Path) -> None:
    """CSV loader từ chối path trỏ tới directory."""

    directory = tmp_path / "csv-directory"
    directory.mkdir()

    with pytest.raises(InvalidDatasetError):
        load_csv(directory)


def test_load_csv_rejects_non_csv_extension(tmp_path: Path) -> None:
    """CSV loader từ chối extension không phải CSV."""

    path = tmp_path / "sample.txt"
    path.write_text("id,name\n1,Alice\n", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        load_csv(path)


def test_load_csv_rejects_unsupported_config_key(tmp_path: Path) -> None:
    """CSV loader từ chối key configuration không nằm trong allow-list."""

    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,Alice\n", encoding="utf-8")

    with pytest.raises(InvalidConfigurationError):
        load_csv(path, config={"unknown_option": True})


def test_load_csv_raises_for_empty_file(tmp_path: Path) -> None:
    """CSV rỗng được ánh xạ thành DatasetParsingError."""

    path = tmp_path / "empty.csv"
    path.write_bytes(b"")

    with pytest.raises(DatasetParsingError):
        load_csv(path)


def test_load_csv_handles_header_only_file(tmp_path: Path) -> None:
    """CSV chỉ có header vẫn được load thành DataFrame rỗng hợp lệ."""

    path = tmp_path / "header-only.csv"
    path.write_text("id,name,value\n", encoding="utf-8")

    actual, result = load_csv(path)

    assert actual.shape == (0, 3)
    _assert_metadata(
        result,
        path=path,
        file_format="csv",
        rows=0,
        columns=3,
    )


def test_load_csv_wraps_encoding_error(tmp_path: Path) -> None:
    """Byte không phải UTF-8 được ánh xạ thành DatasetParsingError."""

    path = tmp_path / "invalid-utf8.csv"
    path.write_bytes(b"id,name\n1,\xff\n")

    with pytest.raises(DatasetParsingError):
        load_csv(path, encoding="utf-8")


def test_load_csv_does_not_modify_source_file(tmp_path: Path) -> None:
    """Load CSV không thay đổi bytes của file nguồn."""

    path = tmp_path / "immutable.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")
    before = _file_sha256(path)

    load_csv(path)

    after = _file_sha256(path)
    assert before == after


def test_load_csv_is_deterministic(tmp_path: Path) -> None:
    """Load cùng một CSV hai lần cho DataFrame và metadata tương đương."""

    path = tmp_path / "deterministic.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")

    first_df, first_result = load_csv(path)
    second_df, second_result = load_csv(path)

    pd.testing.assert_frame_equal(first_df, second_df)
    assert first_result == second_result


def test_load_csv_accepts_uppercase_extension(tmp_path: Path) -> None:
    """CSV loader chấp nhận extension viết hoa nhờ normalize bằng lower()."""

    path = tmp_path / "SAMPLE.CSV"
    expected = _sample_dataframe()
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_csv(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="csv",
        rows=3,
        columns=3,
    )


def test_load_excel_returns_dataframe_and_metadata(tmp_path: Path) -> None:
    """Excel hợp lệ trả DataFrame của sheet đầu tiên và metadata đầy đủ."""

    path = tmp_path / "sample.xlsx"
    expected = _sample_dataframe()
    _write_excel_workbook(path)

    actual, result = load_excel(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="excel",
        rows=3,
        columns=3,
    )
    _assert_result_is_json_serializable(result)


def test_load_excel_uses_first_sheet_when_sheet_name_is_none(tmp_path: Path) -> None:
    """Excel dùng SheetA, sheet đầu tiên, khi sheet_name là None."""

    path = tmp_path / "multi-sheet.xlsx"
    _write_excel_workbook(path)

    actual, _ = load_excel(path, sheet_name=None)

    pd.testing.assert_frame_equal(actual, _sample_dataframe())


def test_load_excel_loads_sheet_by_name(tmp_path: Path) -> None:
    """Excel load đúng sheet khi truyền tên sheet."""

    path = tmp_path / "named-sheet.xlsx"
    _write_excel_workbook(path)
    expected = pd.DataFrame(
        {
            "id": [10, 20],
            "name": ["Delta", "Echo"],
            "value": [100.5, 225.25],
        }
    )

    actual, _ = load_excel(path, sheet_name="SheetB")

    pd.testing.assert_frame_equal(actual, expected)


def test_load_excel_loads_sheet_by_index(tmp_path: Path) -> None:
    """Excel load đúng sheet khi truyền index."""

    path = tmp_path / "indexed-sheet.xlsx"
    _write_excel_workbook(path)
    expected = pd.DataFrame(
        {
            "id": [10, 20],
            "name": ["Delta", "Echo"],
            "value": [100.5, 225.25],
        }
    )

    actual, _ = load_excel(path, sheet_name=1)

    pd.testing.assert_frame_equal(actual, expected)


def test_load_excel_is_deterministic(tmp_path: Path) -> None:
    """Load cùng workbook hai lần cho DataFrame và metadata tương đương."""

    path = tmp_path / "deterministic.xlsx"
    _write_excel_workbook(path)

    first_df, first_result = load_excel(path)
    second_df, second_result = load_excel(path)

    pd.testing.assert_frame_equal(first_df, second_df)
    assert first_result == second_result


def test_load_excel_handles_header_only_sheet(tmp_path: Path) -> None:
    """Excel sheet chỉ có header vẫn được load thành bảng rỗng hợp lệ."""

    path = tmp_path / "header-only.xlsx"
    pd.DataFrame(columns=["id", "name", "value"]).to_excel(
        path,
        sheet_name="SheetA",
        index=False,
        engine="openpyxl",
    )

    actual, result = load_excel(path)

    assert actual.shape == (0, 3)
    _assert_metadata(
        result,
        path=path,
        file_format="excel",
        rows=0,
        columns=3,
    )


def test_load_excel_rejects_unknown_sheet_name(tmp_path: Path) -> None:
    """Tên sheet không tồn tại được xem là InvalidConfigurationError."""

    path = tmp_path / "unknown-sheet.xlsx"
    _write_excel_workbook(path)

    with pytest.raises(InvalidConfigurationError):
        load_excel(path, sheet_name="MissingSheet")


def test_load_excel_rejects_out_of_range_sheet_index(tmp_path: Path) -> None:
    """Sheet index ngoài phạm vi được xem là InvalidConfigurationError."""

    path = tmp_path / "invalid-index.xlsx"
    _write_excel_workbook(path)

    with pytest.raises(InvalidConfigurationError):
        load_excel(path, sheet_name=99)


def test_load_excel_raises_for_missing_file(tmp_path: Path) -> None:
    """Excel loader raise FileNotFoundToolError khi file không tồn tại."""

    with pytest.raises(FileNotFoundToolError):
        load_excel(tmp_path / "missing.xlsx")


def test_load_excel_rejects_directory_path(tmp_path: Path) -> None:
    """Excel loader từ chối path trỏ tới directory."""

    directory = tmp_path / "excel-directory"
    directory.mkdir()

    with pytest.raises(InvalidDatasetError):
        load_excel(directory)


def test_load_excel_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Excel loader từ chối extension không được hỗ trợ."""

    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,Alice\n", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        load_excel(path)


def test_load_excel_rejects_unsupported_config_key(tmp_path: Path) -> None:
    """Excel loader từ chối key configuration không nằm trong allow-list."""

    path = tmp_path / "sample.xlsx"
    _write_excel_workbook(path)

    with pytest.raises(InvalidConfigurationError):
        load_excel(path, config={"unknown_option": True})


def test_load_excel_wraps_corrupted_workbook_error(tmp_path: Path) -> None:
    """Workbook hỏng được ánh xạ thành DatasetParsingError."""

    path = tmp_path / "corrupted.xlsx"
    path.write_bytes(b"this-is-not-an-xlsx-workbook")

    with pytest.raises(DatasetParsingError):
        load_excel(path)


def test_load_excel_does_not_modify_source_file(tmp_path: Path) -> None:
    """Load Excel không thay đổi bytes của workbook nguồn."""

    path = tmp_path / "immutable.xlsx"
    _write_excel_workbook(path)
    before = _file_sha256(path)

    load_excel(path)

    after = _file_sha256(path)
    assert before == after


def test_load_excel_accepts_uppercase_extension(tmp_path: Path) -> None:
    """Excel loader chấp nhận extension viết hoa nhờ normalize bằng lower()."""

    path = tmp_path / "SAMPLE.XLSX"
    _write_excel_workbook(path)

    actual, result = load_excel(path)

    pd.testing.assert_frame_equal(actual, _sample_dataframe())
    _assert_metadata(
        result,
        path=path,
        file_format="excel",
        rows=3,
        columns=3,
    )


def test_load_parquet_returns_dataframe_and_metadata(tmp_path: Path) -> None:
    """Parquet hợp lệ trả DataFrame đúng và metadata đầy đủ."""

    path = tmp_path / "sample.parquet"
    expected = _sample_dataframe()
    expected.to_parquet(path, index=False)

    actual, result = load_parquet(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="parquet",
        rows=3,
        columns=3,
    )
    _assert_result_is_json_serializable(result)


def test_load_parquet_handles_empty_table(tmp_path: Path) -> None:
    """Parquet có schema nhưng không có row vẫn được load thành công."""

    path = tmp_path / "empty-table.parquet"
    empty = pd.DataFrame(
        {
            "id": pd.Series(dtype="int64"),
            "name": pd.Series(dtype="string"),
            "value": pd.Series(dtype="float64"),
        }
    )
    empty.to_parquet(path, index=False)

    actual, result = load_parquet(path)

    assert actual.shape == (0, 3)
    _assert_metadata(
        result,
        path=path,
        file_format="parquet",
        rows=0,
        columns=3,
    )


def test_load_parquet_raises_for_missing_file(tmp_path: Path) -> None:
    """Parquet loader raise FileNotFoundToolError khi file không tồn tại."""

    with pytest.raises(FileNotFoundToolError):
        load_parquet(tmp_path / "missing.parquet")


def test_load_parquet_rejects_directory_path(tmp_path: Path) -> None:
    """Parquet loader từ chối path trỏ tới directory."""

    directory = tmp_path / "parquet-directory"
    directory.mkdir()

    with pytest.raises(InvalidDatasetError):
        load_parquet(directory)


def test_load_parquet_rejects_non_parquet_extension(tmp_path: Path) -> None:
    """Parquet loader từ chối extension không phải Parquet."""

    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,Alice\n", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        load_parquet(path)


def test_load_parquet_rejects_unsupported_config_key(tmp_path: Path) -> None:
    """Parquet loader từ chối key configuration không nằm trong allow-list."""

    path = tmp_path / "sample.parquet"
    _sample_dataframe().to_parquet(path, index=False)

    with pytest.raises(InvalidConfigurationError):
        load_parquet(path, config={"unknown_option": True})


def test_load_parquet_wraps_corrupted_file_error(tmp_path: Path) -> None:
    """File Parquet hỏng được ánh xạ thành DatasetParsingError."""

    path = tmp_path / "corrupted.parquet"
    path.write_bytes(b"this-is-not-a-parquet-file")

    with pytest.raises(DatasetParsingError):
        load_parquet(path)


def test_load_parquet_does_not_modify_source_file(tmp_path: Path) -> None:
    """Load Parquet không thay đổi bytes của file nguồn."""

    path = tmp_path / "immutable.parquet"
    _sample_dataframe().to_parquet(path, index=False)
    before = _file_sha256(path)

    load_parquet(path)

    after = _file_sha256(path)
    assert before == after


def test_load_parquet_is_deterministic(tmp_path: Path) -> None:
    """Load cùng Parquet hai lần cho DataFrame và metadata tương đương."""

    path = tmp_path / "deterministic.parquet"
    _sample_dataframe().to_parquet(path, index=False)

    first_df, first_result = load_parquet(path)
    second_df, second_result = load_parquet(path)

    pd.testing.assert_frame_equal(first_df, second_df)
    assert first_result == second_result


def test_load_parquet_accepts_uppercase_extension(tmp_path: Path) -> None:
    """Parquet loader chấp nhận extension viết hoa nhờ normalize bằng lower()."""

    path = tmp_path / "SAMPLE.PARQUET"
    expected = _sample_dataframe()
    expected.to_parquet(path, index=False)

    actual, result = load_parquet(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="parquet",
        rows=3,
        columns=3,
    )


# ============================================================
# load_dataset dispatcher
# ============================================================


def test_load_dataset_dispatches_csv_by_extension(tmp_path: Path) -> None:
    """Dispatcher chọn load_csv cho file có extension .csv."""

    path = tmp_path / "dispatch.csv"
    expected = _sample_dataframe()
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_dataset(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="csv",
        rows=3,
        columns=3,
    )


def test_load_dataset_dispatches_excel_by_extension(tmp_path: Path) -> None:
    """Dispatcher chọn load_excel cho file có extension .xlsx."""

    path = tmp_path / "dispatch.xlsx"
    _write_excel_workbook(path)

    actual, result = load_dataset(path)

    pd.testing.assert_frame_equal(actual, _sample_dataframe())
    _assert_metadata(
        result,
        path=path,
        file_format="excel",
        rows=3,
        columns=3,
    )


def test_load_dataset_dispatches_parquet_by_extension(tmp_path: Path) -> None:
    """Dispatcher chọn load_parquet cho file có extension .parquet."""

    path = tmp_path / "dispatch.parquet"
    expected = _sample_dataframe()
    expected.to_parquet(path, index=False)

    actual, result = load_dataset(path)

    pd.testing.assert_frame_equal(actual, expected)
    _assert_metadata(
        result,
        path=path,
        file_format="parquet",
        rows=3,
        columns=3,
    )


def test_load_dataset_accepts_matching_explicit_format(tmp_path: Path) -> None:
    """Dispatcher load thành công khi format tường minh khớp extension."""

    path = tmp_path / "explicit-format.csv"
    expected = _sample_dataframe()
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_dataset(path, format="csv")

    pd.testing.assert_frame_equal(actual, expected)
    assert result.reference.format == "csv"


def test_load_dataset_rejects_format_extension_conflict(tmp_path: Path) -> None:
    """Dispatcher từ chối format tường minh xung đột với extension."""

    path = tmp_path / "conflict.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")

    with pytest.raises(InvalidConfigurationError):
        load_dataset(path, format="excel")


def test_load_dataset_rejects_unsupported_explicit_format(tmp_path: Path) -> None:
    """Dispatcher từ chối format tường minh không được hỗ trợ."""

    path = tmp_path / "unsupported-format.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        load_dataset(path, format="pdf")


def test_load_dataset_rejects_unsupported_extension(
    unsupported_format_path: Path,
) -> None:
    """Dispatcher từ chối extension không được hỗ trợ."""

    with pytest.raises(UnsupportedFormatError):
        load_dataset(unsupported_format_path)


def test_load_dataset_rejects_missing_extension_when_format_is_not_given(
    tmp_path: Path,
) -> None:
    """Dispatcher từ chối file không có extension khi thiếu format tường minh."""

    path = tmp_path / "dataset"
    path.write_text("id,name\n1,Alice\n", encoding="utf-8")

    with pytest.raises(UnsupportedFormatError):
        load_dataset(path)


def test_load_dataset_passes_encoding_to_csv(tmp_path: Path) -> None:
    """Dispatcher chuyển encoding xuống CSV loader."""

    path = tmp_path / "encoding.csv"
    expected = pd.DataFrame({"id": [1], "name": ["Alice"]})
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_dataset(path, encoding="utf-8")

    pd.testing.assert_frame_equal(actual, expected)
    assert result.reference.format == "csv"


def test_load_dataset_rejects_encoding_for_non_csv(tmp_path: Path) -> None:
    """Dispatcher không cho dùng encoding riêng của CSV cho Excel."""

    path = tmp_path / "encoding.xlsx"
    _write_excel_workbook(path)

    with pytest.raises(InvalidConfigurationError):
        load_dataset(path, encoding="utf-8")


def test_load_dataset_passes_sheet_name_to_excel(tmp_path: Path) -> None:
    """Dispatcher chuyển sheet_name xuống Excel loader."""

    path = tmp_path / "selected-sheet.xlsx"
    _write_excel_workbook(path)
    expected = pd.DataFrame(
        {
            "id": [10, 20],
            "name": ["Delta", "Echo"],
            "value": [100.5, 225.25],
        }
    )

    actual, result = load_dataset(path, sheet_name="SheetB")

    pd.testing.assert_frame_equal(actual, expected)
    assert result.reference.format == "excel"


def test_load_dataset_rejects_sheet_name_for_non_excel(tmp_path: Path) -> None:
    """Dispatcher không cho dùng sheet_name cho CSV."""

    path = tmp_path / "sheet-name.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")

    with pytest.raises(InvalidConfigurationError):
        load_dataset(path, sheet_name="SheetA")


def test_load_dataset_passes_config_to_csv(tmp_path: Path) -> None:
    """Dispatcher chuyển config xuống CSV loader."""

    path = tmp_path / "semicolon.csv"
    path.write_text("id;name\n1;Alice\n", encoding="utf-8")
    expected = pd.DataFrame({"id": [1], "name": ["Alice"]})

    actual, result = load_dataset(path, config={"sep": ";"})

    pd.testing.assert_frame_equal(actual, expected)
    assert result.reference.format == "csv"


def test_load_dataset_is_deterministic(tmp_path: Path) -> None:
    """Dispatcher cho kết quả DataFrame và metadata giống nhau qua hai lần gọi."""

    path = tmp_path / "dispatcher-deterministic.csv"
    _sample_dataframe().to_csv(path, index=False, encoding="utf-8")

    first_df, first_result = load_dataset(path)
    second_df, second_result = load_dataset(path)

    pd.testing.assert_frame_equal(first_df, second_df)
    assert first_result == second_result


def test_load_dataset_accepts_uppercase_extension(tmp_path: Path) -> None:
    """Dispatcher normalize suffix viết hoa và chọn đúng CSV loader."""

    path = tmp_path / "SAMPLE.CSV"
    expected = _sample_dataframe()
    expected.to_csv(path, index=False, encoding="utf-8")

    actual, result = load_dataset(path)

    pd.testing.assert_frame_equal(actual, expected)
    assert result.reference.format == "csv"


def test_load_csv_result_is_json_serializable(tmp_path: Path) -> None:
    """Structured loader metadata phải JSON-serializable."""

    path = tmp_path / "dataset.csv"
    path.write_text(
        "id,city\n1,HN\n2,HCM\n",
        encoding="utf-8",
    )

    _, result = load_csv(path)

    payload = result.model_dump(mode="json")
    serialized = json.dumps(payload)

    assert isinstance(serialized, str)
    assert isinstance(json.loads(serialized), dict)
