__all__ = [
    "DataToolError",
    "FileNotFoundToolError",
    "UnsupportedFormatError",
    "InvalidDatasetError",
    "DatasetParsingError",
    "InvalidConfigurationError",
]


class DataToolError(Exception):
    """Lớp cơ sở cho các lỗi dự kiến của deterministic data tools."""

    error_code = "DATA_TOOL_ERROR"


class FileNotFoundToolError(DataToolError):
    """Được raise khi file input được yêu cầu không tồn tại."""

    error_code = "FILE_NOT_FOUND"


class UnsupportedFormatError(DataToolError):
    """Được raise khi format hoặc extension của file không được hỗ trợ."""

    error_code = "UNSUPPORTED_FORMAT"


class InvalidDatasetError(DataToolError):
    """Được raise khi dataset input vi phạm precondition của loader/tool."""

    error_code = "INVALID_DATASET"


class DatasetParsingError(DataToolError):
    """Được raise khi file được hỗ trợ không thể parse thành công."""

    error_code = "DATASET_PARSE_ERROR"


class InvalidConfigurationError(DataToolError):
    """Được raise khi configuration của loader hoặc quality tool không hợp lệ."""

    error_code = "INVALID_CONFIGURATION"