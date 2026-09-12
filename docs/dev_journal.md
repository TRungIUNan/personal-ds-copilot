# Nhật ký phát triển

Đây là nhật ký học tập, không phải bản ghi chi tiết implementation. Nội dung
tập trung vào lý do phía sau mỗi contract và bằng chứng từ test/evaluation.

Các thuật ngữ technical được giữ nguyên khi cần để đồng bộ với code, test và
output của tool.

## Bộ khung Week 01

- Ngày:
- Nhiệm vụ:
- Điều đã học:
- Quyết định thiết kế:
- Quy ước đã chọn (null, rate, dtype, tie, threshold):
- Test đã thêm:
- Bằng chứng:
- Câu hỏi còn mở:
- Bước tiếp theo:

## W01-T08 — Đánh giá và tài liệu

- Ngày: 2026-09-09
- Nhiệm vụ: Ghi lại định nghĩa evaluation Week 01, bằng chứng, các lệnh chạy và
  những giới hạn đã biết.
- Điều đã học: Kết quả của một quality gate không đồng nghĩa với metric về
  tool correctness. Metric cần có tập test rõ ràng cùng tử số và mẫu số có thể
  tái lập.
- Quyết định thiết kế: Giữ bản ghi evaluation trong
  docs/week01_evaluation.md và giữ README tập trung vào cài đặt, cách dùng,
  các check và tính an toàn.
- Quy ước đã chọn: Không công bố phần trăm khi môi trường hiện tại không
  thể chạy test runner. Tách behavioral test khỏi schema, lint, type-check và
  compilation gate.
- Test đã thêm: Không thay đổi production hoặc runtime test trong T08. Bản ghi
  này audit test và fixture từ W01-T03 đến W01-T07.
- Bằng chứng: Interpreter hiện tại pass compileall. pytest, pandas, Pydantic,
  Ruff và mypy không có trong shell này. Brief T07 báo cáo rằng các gate đó đã
  pass trong môi trường phát triển của developer.
- Câu hỏi còn mở: Chạy lại các lệnh đã ghi nhận trong môi trường phát triển
  được cài đặt đầy đủ và điền kết quả của ba metric từ output test thực tế.
- Bước tiếp theo: Hoàn tất runtime evaluation trước khi bắt đầu W01-T09.

## Gợi ý câu hỏi cho mỗi task

1. Tool này giải quyết vấn đề gì?
2. Contract input/output nhỏ nhất nhưng hữu ích là gì?
3. Edge case nào buộc phải đưa ra quyết định thiết kế?
4. Đã chứng minh dữ liệu nguồn không bị mutate như thế nào?
5. Giới hạn nào vẫn còn?

Không đánh dấu một task hoàn thành chỉ vì file đã tồn tại.
