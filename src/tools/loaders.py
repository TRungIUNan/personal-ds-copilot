"""
W01-T03 — Loader đọc file

MỤC ĐÍCH
--------
Định nghĩa các entry point deterministic để load file CSV, Excel và Parquet mà
không sửa file nguồn, đồng thời chuẩn hóa boundary lỗi và metadata trả về.

KIẾN THỨC CẦN HỌC
------------------
1. Cách pandas giao việc parse CSV/Excel/Parquet cho engine riêng của từng format.
2. Cách validate path và extension được hỗ trợ trước khi đọc.
3. Cách tách dữ liệu đã parse khỏi metadata load có thể chuyển sang JSON.
4. Cách phân loại lỗi không tìm thấy file, format không hỗ trợ, encoding và parse.

THỨ TỰ TRIỂN KHAI
------------------
1. Định nghĩa return contract và quyết định dùng tuple hay result object.
2. Triển khai đường đi CSV hợp lệ nhỏ nhất và viết test trước.
3. Thêm behavior cho Excel sheet và configuration tường minh.
4. Thêm behavior Parquet và xử lý file hỏng.
5. Chỉ thêm dispatcher dùng chung sau khi hiểu rõ từng loader riêng.
6. Chuẩn hóa exception dự kiến theo exception hierarchy của Week 01.

RÀNG BUỘC QUAN TRỌNG
---------------------
- Không mutate file nguồn hoặc DataFrame nguồn được trả về tại chỗ.
- Không đoán encoding vô hạn; phải quy định behavior encoding rõ ràng.
- Giữ loader deterministic và độc lập với LLM/LangGraph.
- Không thêm caching, agent hoặc orchestration trong Week 01.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from zipfile import BadZipFile

import pandas as pd
from pyarrow import ArrowInvalid

from .exceptions import (
    DatasetParsingError,
    FileNotFoundToolError,
    InvalidConfigurationError,
    InvalidDatasetError,
    UnsupportedFormatError,
)
from .schemas import DatasetLoadResult, DatasetReference


def load_csv(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    config: Mapping[str, Any] | None = None,
) -> tuple[pd.DataFrame, DatasetLoadResult]:
    """Load một file CSV và trả về DataFrame cùng metadata có cấu trúc.

    Parameters
    ----------
    path:
        Đường dẫn tới file CSV.

    encoding:
        Encoding dùng để đọc file. Mặc định là UTF-8.

    config:
        Các tùy chọn đọc CSV được cho phép truyền thêm cho pandas.

    Returns
    -------
    tuple[pd.DataFrame, DatasetLoadResult]
        DataFrame đã đọc và metadata của quá trình load.

    Raises
    ------
    FileNotFoundToolError
        Khi file không tồn tại.

    InvalidDatasetError
        Khi path không trỏ tới một file hợp lệ.

    UnsupportedFormatError
        Khi extension không phải .csv.

    InvalidConfigurationError
        Khi config chứa option không được hỗ trợ.

    DatasetParsingError
        Khi CSV không thể được parse hoặc encoding không đúng.
    """
    # 1. Chuẩn hóa path
    path_obj = Path(path)

    # 2. Validate path

    if not path_obj.exists():
        raise FileNotFoundToolError(
            f"Không tìm thấy file CSV: {path_obj}"
        )

    if not path_obj.is_file():
        raise InvalidDatasetError(
            f"Path không trỏ tới một file hợp lệ: {path_obj}"
        )

    # 3. Validate extension

    if path_obj.suffix.lower() != ".csv":
        raise UnsupportedFormatError(
            f"load_csv() chỉ hỗ trợ file .csv, nhận được: "
            f"{path_obj.suffix or '<không có extension>'}"
        )

    # 4. Validate config

    allowed_config_keys = {
        "sep",
        "header",
        "names",
        "dtype",
        "na_values",
        "keep_default_na",
        "usecols",
        "nrows",
    }

    csv_config = dict(config or {})

    unsupported_keys = set(csv_config) - allowed_config_keys

    if unsupported_keys:
        raise InvalidConfigurationError(
            "CSV config chứa option không được hỗ trợ: "
            f"{sorted(unsupported_keys)}"
        )

    # 5. Parse CSV

    try:
        df = pd.read_csv(
            path_obj,
            encoding=encoding,
            **csv_config,
        )

    except UnicodeDecodeError as exc:
        raise DatasetParsingError(
            f"Không thể decode CSV bằng encoding '{encoding}'."
        ) from exc

    except pd.errors.EmptyDataError as exc:
        raise DatasetParsingError(
            "CSV không chứa dữ liệu hoặc header có thể parse."
        ) from exc

    except pd.errors.ParserError as exc:
        raise DatasetParsingError(
            "CSV có cấu trúc không hợp lệ và không thể parse."
        ) from exc

    # 6. Tạo metadata

    rows, columns = df.shape

    reference = DatasetReference(
        path=str(path_obj),
        format="csv",
        rows=rows,
        columns=columns,
    )

    result = DatasetLoadResult(
        reference=reference,
        warnings=[],
    )

    # 7. Return

    return df, result

def load_excel(
    path: str | Path,
    *,
    sheet_name: str | int | None = None,
    config: Mapping[str, Any] | None = None,
) -> tuple[pd.DataFrame, DatasetLoadResult]:
    """Load một Excel sheet và trả về DataFrame cùng metadata có cấu trúc.

    Parameters
    ----------
    path:
        Đường dẫn tới Excel workbook.

    sheet_name:
        Tên hoặc vị trí sheet cần đọc.
        Nếu None, sử dụng sheet đầu tiên.

    config:
        Các tùy chọn Excel reader được cho phép.

    Returns
    -------
    tuple[pd.DataFrame, DatasetLoadResult]
        DataFrame của sheet đã chọn và metadata load.
    """

    # 1. Chuẩn hóa path

    path_obj = Path(path)

    # 2. Validate path

    if not path_obj.exists():
        raise FileNotFoundToolError(
            f"Không tìm thấy file Excel: {path_obj}"
        )

    if not path_obj.is_file():
        raise InvalidDatasetError(
            f"Path không trỏ tới một file hợp lệ: {path_obj}"
        )

    # 3. Validate extension

    supported_extensions = {".xlsx", ".xlsm"}

    if path_obj.suffix.lower() not in supported_extensions:
        raise UnsupportedFormatError(
            "load_excel() chỉ hỗ trợ file .xlsx hoặc .xlsm, "
            f"nhận được: {path_obj.suffix or '<không có extension>'}"
        )

    # 4. Validate config

    allowed_config_keys = {
        "header",
        "names",
        "dtype",
        "na_values",
        "keep_default_na",
        "usecols",
        "nrows",
        "skiprows",
    }

    excel_config = dict(config or {})

    unsupported_keys = set(excel_config) - allowed_config_keys

    if unsupported_keys:
        raise InvalidConfigurationError(
            "Excel config chứa option không được hỗ trợ: "
            f"{sorted(unsupported_keys)}"
        )

    # 5. Xác định sheet

    try:
        with pd.ExcelFile(path_obj, engine="openpyxl") as workbook:
            available_sheets = workbook.sheet_names

            if not available_sheets:
                raise InvalidDatasetError(
                    "Workbook không chứa sheet nào."
                )

            if sheet_name is None:
                selected_sheet: str | int = available_sheets[0]

            elif isinstance(sheet_name, str):
                if sheet_name not in available_sheets:
                    raise InvalidConfigurationError(
                        f"Không tồn tại sheet '{sheet_name}'. "
                        f"Các sheet hiện có: {available_sheets}"
                    )

                selected_sheet = sheet_name

            elif isinstance(sheet_name, int):
                if sheet_name < 0 or sheet_name >= len(available_sheets):
                    raise InvalidConfigurationError(
                        f"Sheet index {sheet_name} nằm ngoài phạm vi hợp lệ."
                    )

                selected_sheet = sheet_name

            else:
                raise InvalidConfigurationError(
                    "sheet_name phải là str, int hoặc None."
                )

            # ========================================================
            # 6. Parse sheet
            # ========================================================

            df = pd.read_excel(
                workbook,
                sheet_name=selected_sheet,
                **excel_config,
            )

    except (InvalidConfigurationError, InvalidDatasetError):
        raise

    except ImportError as exc:
        raise DatasetParsingError(
            "Không thể đọc Excel do thiếu dependency openpyxl."
        ) from exc

    except (BadZipFile, ValueError, OSError) as exc:
        raise DatasetParsingError(
            "Workbook Excel không thể được parse."
        ) from exc

    # 7. Metadata

    rows, columns = df.shape

    reference = DatasetReference(
        path=str(path_obj),
        format="excel",
        rows=rows,
        columns=columns,
    )

    result = DatasetLoadResult(
        reference=reference,
        warnings=[],
    )

    return df, result


def load_parquet(
    path: str | Path,
    *,
    config: Mapping[str, Any] | None = None,
) -> tuple[pd.DataFrame, DatasetLoadResult]:
    """Load file Parquet và trả về DataFrame cùng metadata có cấu trúc.

    Parameters
    ----------
    path:
        Đường dẫn tới file Parquet.

    config:
        Các tùy chọn Parquet reader được cho phép.

    Returns
    -------
    tuple[pd.DataFrame, DatasetLoadResult]
        DataFrame đã parse và metadata load.
    """

    # 1. Chuẩn hóa path

    path_obj = Path(path)

    # 2. Validate path

    if not path_obj.exists():
        raise FileNotFoundToolError(
            f"Không tìm thấy file Parquet: {path_obj}"
        )

    if not path_obj.is_file():
        raise InvalidDatasetError(
            f"Path không trỏ tới một file hợp lệ: {path_obj}"
        )

    # 3. Validate extension

    if path_obj.suffix.lower() != ".parquet":
        raise UnsupportedFormatError(
            "load_parquet() chỉ hỗ trợ file .parquet, "
            f"nhận được: {path_obj.suffix or '<không có extension>'}"
        )

    # 4. Validate config

    allowed_config_keys = {
        "columns",
        "filters",
        "engine",
    }

    parquet_config = dict(config or {})

    unsupported_keys = set(parquet_config) - allowed_config_keys

    if unsupported_keys:
        raise InvalidConfigurationError(
            "Parquet config chứa option không được hỗ trợ: "
            f"{sorted(unsupported_keys)}"
        )

    # 5. Default engine

    parquet_config.setdefault(
        "engine",
        "pyarrow",
    )

    # 6. Parse Parquet

    try:
        df = pd.read_parquet(
            path_obj,
            **parquet_config,
        )

    except ImportError as exc:
        raise DatasetParsingError(
            "Không thể đọc Parquet do thiếu dependency/engine."
        ) from exc

    except (ArrowInvalid, ValueError, OSError) as exc:
        raise DatasetParsingError(
            "File Parquet không thể được parse."
        ) from exc

    # 7. Metadata

    rows, columns = df.shape

    reference = DatasetReference(
        path=str(path_obj),
        format="parquet",
        rows=rows,
        columns=columns,
    )

    result = DatasetLoadResult(
        reference=reference,
        warnings=[],
    )

    return df, result


def load_dataset(
    path: str | Path,
    *,
    format: str | None = None,
    encoding: str | None = None,
    sheet_name: str | int | None = None,
    config: Mapping[str, Any] | None = None,
) -> tuple[pd.DataFrame, DatasetLoadResult]:
    """Load dataset bằng loader phù hợp với CSV, Excel hoặc Parquet.

    Parameters
    ----------
    path:
        Đường dẫn tới dataset.

    format:
        Format tường minh, optional.
        Các giá trị hỗ trợ:
        - "csv"
        - "excel"
        - "parquet"

        Nếu không truyền, format được xác định từ extension.

    encoding:
        Encoding dành riêng cho CSV.

    sheet_name:
        Sheet selector dành riêng cho Excel.

    config:
        Configuration được chuyển tiếp cho loader tương ứng.

    Returns
    -------
    tuple[pd.DataFrame, DatasetLoadResult]
        DataFrame đã load và structured metadata.

    Raises
    ------
    UnsupportedFormatError
        Khi format hoặc extension không được hỗ trợ.

    InvalidConfigurationError
        Khi format xung đột với extension hoặc truyền argument
        không phù hợp với loại file.
    """

    # 1. Chuẩn hóa path

    path_obj = Path(path)

    # 2. Xác định format từ extension

    extension = path_obj.suffix.lower()

    extension_to_format = {
        ".csv": "csv",
        ".xlsx": "excel",
        ".xlsm": "excel",
        ".parquet": "parquet",
    }

    detected_format = extension_to_format.get(extension)

    # 3. Chuẩn hóa format tường minh

    normalized_format: str | None = None

    if format is not None:
        normalized_format = format.strip().lower()

        format_aliases = {
            "csv": "csv",
            "excel": "excel",
            "xlsx": "excel",
            "xlsm": "excel",
            "parquet": "parquet",
        }

        normalized_format = format_aliases.get(normalized_format)

        if normalized_format is None:
            raise UnsupportedFormatError(
                f"Format không được hỗ trợ: {format}"
            )

    # 4. Chọn format cuối cùng

    if normalized_format is None:
        if detected_format is None:
            raise UnsupportedFormatError(
                "Không thể xác định format từ extension: "
                f"{extension or '<không có extension>'}"
            )

        selected_format = detected_format

    else:
        selected_format = normalized_format

        # Nếu extension đã nhận diện được thì format tường minh
        # phải khớp với extension.
        if detected_format is not None and selected_format != detected_format:
            raise InvalidConfigurationError(
                "Format tường minh không khớp với extension của file. "
                f"format={selected_format}, extension={extension}"
            )

        # Nếu extension tồn tại nhưng không được hỗ trợ,
        # không âm thầm bỏ qua chỉ vì caller truyền format.
        if detected_format is None and extension:
            raise UnsupportedFormatError(
                f"Extension không được hỗ trợ: {extension}"
            )

    # 5. Validate argument riêng của từng format

    if selected_format != "csv" and encoding is not None:
        raise InvalidConfigurationError(
            "encoding chỉ được sử dụng khi load CSV."
        )

    if selected_format != "excel" and sheet_name is not None:
        raise InvalidConfigurationError(
            "sheet_name chỉ được sử dụng khi load Excel."
        )

    # 6. Dispatch

    if selected_format == "csv":
        return load_csv(
            path_obj,
            encoding=encoding or "utf-8",
            config=config,
        )

    if selected_format == "excel":
        return load_excel(
            path_obj,
            sheet_name=sheet_name,
            config=config,
        )

    if selected_format == "parquet":
        return load_parquet(
            path_obj,
            config=config,
        )

    # Defensive fallback.
    # Về logic bình thường sẽ không tới đây.
    raise UnsupportedFormatError(
        f"Format không được hỗ trợ: {selected_format}"
    )
