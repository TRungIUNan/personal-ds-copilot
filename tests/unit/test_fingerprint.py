"""
W01-T09 — Kiểm thử behavior fingerprint của file

Implementation được cố ý trì hoãn. Các test này xác định evidence cần có để học
về content identity, đọc theo chunk và metadata ổn định.
"""

from src.tools import fingerprint  # noqa: F401


def test_same_file_content_produces_same_fingerprint(tmp_path) -> None:
    """Tạo fingerprint lặp lại trên byte không đổi phải cho kết quả ổn định."""

    # TODO W01-T09: ghi byte đã biết và so sánh mã fingerprint qua các lần gọi.
    raise NotImplementedError("TODO W01-T09: kiểm thử fingerprint ổn định")


def test_changed_file_content_changes_fingerprint(tmp_path) -> None:
    """Thay đổi content file phải làm content identity thay đổi."""

    # TODO W01-T09: thay đổi byte kiểm thử và so sánh digest/contract.
    raise NotImplementedError("TODO W01-T09: kiểm thử fingerprint khi nội dung thay đổi")


def test_filename_alone_is_not_file_identity(tmp_path) -> None:
    """Đổi tên content giống nhau phải tuân theo policy content identity đã chọn."""

    # TODO W01-T09: tạo fingerprint cho cùng byte với các tên file khác nhau.
    raise NotImplementedError("TODO W01-T09: kiểm thử filename không phải identity")


def test_fingerprint_uses_bounded_chunk_configuration(tmp_path) -> None:
    """Chunk size được nêu rõ và value không hợp lệ bị từ chối."""

    # TODO W01-T09: kiểm thử chunk size nhỏ và hành vi khi chunk_size không dương.
    raise NotImplementedError("TODO W01-T09: kiểm thử contract đọc theo chunk")


def test_missing_or_unreadable_file_returns_structured_failure(tmp_path) -> None:
    """Input thiếu/không đọc được có behavior error dễ dự đoán."""

    # TODO W01-T09: kiểm tra typed error và context an toàn.
    raise NotImplementedError("TODO W01-T09: kiểm thử đường dẫn fingerprint không hợp lệ")


def test_fingerprint_output_is_json_serializable_and_deterministic(tmp_path) -> None:
    """Fingerprint output có field ổn định và serialize sạch."""

    # TODO W01-T09: chuyển output lặp lại sang JSON và so sánh chúng.
    raise NotImplementedError("TODO W01-T09: kiểm thử serialization/tính tất định của fingerprint")
