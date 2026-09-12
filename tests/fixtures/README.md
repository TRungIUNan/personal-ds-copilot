# Fixture Week 01

Thư mục này không chứa dataset thật hoặc dữ liệu nhạy cảm.

Các fixture Week 01 được định nghĩa dưới dạng DataFrame nhỏ trong
tests/conftest.py hoặc đường dẫn tạm thời do pytest tạo. Mỗi fixture tập trung
vào một behavior và tránh file lớn hoặc dữ liệu nhạy cảm. Các case gồm:

- `normal`
- `empty`
- `all_null_column`
- `duplicate_rows`
- `mixed_dtype`
- `constant_column`
- `high_cardinality_string`
- `possible_id`
- `invalid_path`
- `unsupported_format`

Các fixture file như `invalid_path` và `unsupported_format` chỉ tạo path/file
tạm thời trong test; loader không ghi đè dữ liệu nguồn.
