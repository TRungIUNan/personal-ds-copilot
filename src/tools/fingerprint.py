"""
W01-T09 — Skeleton fingerprint của file

MỤC ĐÍCH
--------
Định nghĩa identity contract ổn định cho file dataset để nhận diện content không
đổi và metadata ổn định qua nhiều lần chạy.

KIẾN THỨC CẦN HỌC
------------------
1. Vì sao chỉ filename không phải là identity đáng tin cậy của dataset.
2. Cách hash mật mã như SHA-256 biểu diễn content của file.
3. Vì sao đọc theo chunk quan trọng với file lớn.
4. Metadata nào đủ ổn định để đưa vào và metadata nào phụ thuộc máy.

THỨ TỰ TRIỂN KHAI
------------------
1. Quyết định fingerprint W01 chỉ dựa trên content hay content cộng metadata
   được document cẩn thận.
2. Quyết định output schema và algorithm identifier.
3. Triển khai hash file nhỏ trước và test bằng byte đã biết.
4. Chỉ thêm đọc theo chunk và metadata ổn định sau khi contract cơ bản chạy đúng.
5. Test file không đổi, đã đổi, được đổi tên, bị thiếu và không đọc được.

RÀNG BUỘC QUAN TRỌNG
---------------------
- Không chỉ dùng filename làm identity.
- Không mặc định đọc toàn bộ file vào memory.
- Không sửa file nguồn.
- Giữ metadata algorithm/version tường minh để phát hiện thay đổi trong tương lai.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def create_file_fingerprint(
    path: str | Path,
    *,
    algorithm: str = "sha256",
    chunk_size: int = 1024 * 1024,
    include_metadata: bool = True,
) -> dict[str, Any]:
    """Tạo fingerprint contract ổn định cho một file.

    Mục đích
    -------
    Nhận diện version của file bằng content và, nếu chọn, metadata ổn định.

    Tham số
    ----------
    path:
        File cần tạo fingerprint.
    algorithm:
        Identifier của hash algorithm. Quyết định algorithm nào được phép và ghi
        identifier vào result.
    chunk_size:
        Số byte đọc mỗi vòng để giới hạn memory sử dụng.
    include_metadata:
        Có đưa metadata ổn định đã chọn cẩn thận vào result hay không.

    Giá trị trả về
    -------
    dict[str, Any]
        Field gợi ý: policy path đã normalize, algorithm, digest, kích thước
        content và metadata ổn định được định nghĩa tường minh.

    Behavior mong đợi
    -----------------
    Cùng content và cùng quy ước metadata đã chọn phải tạo cùng fingerprint.
    Khi content file đổi thì digest phải đổi. Đổi tên file không nên đổi identity
    nếu identity chỉ dựa trên content.

    Trường hợp biên
    ----------
    - path bị thiếu;
    - path là directory thay vì file;
    - file rỗng;
    - file bị thay đổi trong lúc đang đọc;
    - algorithm không được hỗ trợ;
    - chunk size không dương;
    - lỗi permission/read;
    - metadata không ổn định như absolute path phụ thuộc máy.

    Gợi ý triển khai
    --------------------
    1. Validate file và algorithm trước khi đọc.
    2. Đọc byte từng phần bằng chunk size đã chọn.
    3. Định nghĩa metadata có ổn định theo content hay không và loại value biến động.
    4. Trả thông tin algorithm/version cùng với digest.
    5. Không bao giờ chỉ dựa vào filename và không rewrite file.

    Test cần viết
    --------------
    - cùng byte tạo cùng fingerprint;
    - thay đổi một byte content làm fingerprint thay đổi;
    - behavior đổi tên theo quy ước đã chọn;
    - case file rỗng/thiếu/directory/chunk không hợp lệ;
    - JSON serialization và các lần gọi lặp lại có tính tất định.

    Definition of Done
    ------------------
    - Content identity tường minh và có algorithm label.
    - File lớn được xử lý bằng cách đọc có giới hạn.
    - File nguồn vẫn không thay đổi.
    """

    # TODO W01-T09:
    # Bước 1: validate path, algorithm và chunk_size dương.
    # Bước 2: stream bytes của file qua hash implementation đã chọn.
    # Bước 3: chỉ thu thập metadata ổn định, đã document, nếu được yêu cầu.
    # Bước 4: trả về fingerprint contract serialize được sang JSON.
    raise NotImplementedError("TODO W01-T09: triển khai create_file_fingerprint")
