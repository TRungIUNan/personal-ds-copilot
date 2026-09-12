# Đánh giá Week 01

Đây là bản ghi đánh giá cho W01-T08. Phạm vi là lớp công cụ deterministic đã
hoàn thành từ W01-T03 đến W01-T06, cùng với fixture và test W01-T07 làm bằng
chứng về độ bền. Fingerprinting của W01-T09 nằm ngoài phạm vi rõ ràng.

Các thuật ngữ kỹ thuật như loader, inspection, quality, descriptive, fixture,
test, runtime, schema, dtype, DataFrame, exception, metric, gate, pass, skip và
fail được giữ nguyên để đồng bộ với tên module, hàm và output của code.

## Phạm vi

- Loaders: CSV, Excel, Parquet và bộ điều phối format.
- Inspection: shape, dtype, schema, tóm tắt cột và preview có giới hạn.
- Quality: giá trị thiếu, bản ghi trùng, cardinality, cột constant và
  candidate ID.
- Descriptive: thống kê mô tả numeric và categorical.

## Chính sách bằng chứng

Các metric dưới đây chỉ sử dụng test trong repository và các lệnh có thể chạy
lặp lại. Lint, kiểm tra kiểu và compile là các quality gate, nhưng không được
tính vào tool correctness. Các trường hợp skip do portability được báo cáo
riêng và không được tính là lỗi.

Không công bố phần trăm nếu một lần chạy test chưa cung cấp cả tử số và mẫu số.

## Môi trường

Yêu cầu của project khai báo Python 3.11 trở lên, pandas 2 trở lên, Pydantic 2,
pytest 7 trở lên, Ruff 0.6 trở lên và mypy 1.8 trở lên.

Môi trường runtime được ghi nhận: Python 3.11.16, pytest 9.1.1 và Windows
(win32). Các bằng chứng runtime bên dưới đến từ môi trường này.

## Các lệnh đánh giá

Chạy từ thư mục gốc của project trong môi trường phát triển đã được cài đặt:

~~~powershell
python -m pytest tests/unit/test_loaders.py tests/unit/test_inspection.py tests/unit/test_quality.py tests/unit/test_descriptive.py -v
python -m pytest tests/unit/test_tool_schemas.py -v
python -m compileall -q src tests
mypy src tests
ruff check src tests
~~~

Các lệnh trên tạo ra kết quả về behavior, schema, regression, kiểm tra kiểu,
lint và compile được ghi lại bên dưới.

## Các metric

| Metric | Định nghĩa | Kết quả | Bằng chứng |
| --- | --- | --- | --- |
| tool_correctness | Số behavioral test pass chia cho số behavioral test không bị skip đã thực thi trong test_loaders.py, test_inspection.py, test_quality.py và test_descriptive.py. | 100% (362/362 behavioral test không bị skip đã thực thi đều pass) | Behavior suite: 362 pass, 2 skip, 0 fail. |
| exception_correctness | Số test negative-path pass, được chọn theo behavior/tên có missing, raises, rejects, invalid, unsupported, corrupted hoặc wraps, chia cho số negative-path test được đánh giá. | 100% các exception-contract check đã thực thi đều pass; không tự đưa ra mẫu số riêng. | Các assertion typed exception trong bốn file behavior; hai portability skip được báo cáo riêng. |
| schema_validation_rate | Số test Pydantic schema pass chia cho số schema test đã thực thi, với các test JSON serialization làm bằng chứng bổ sung. | 100% (21/21 schema validation test pass) | test_tool_schemas.py: 21 collected, 21 pass, 0 skip, 0 fail. |

Schema contract sử dụng structured result object của Pydantic v2, các field có
constraint khi được định nghĩa, giá trị an toàn cho JSON và field position để
giữ identity ổn định khi có tên cột trùng.

Metric exception cố ý không tự tạo mẫu số X/X: chưa có một lần chạy pytest
riêng chỉ cho exception, và các negative path dạng parameterized chưa được
đếm độc lập trong bản ghi này.

## Bằng chứng về độ bền

Repository có test và fixture cho:

- DataFrame rỗng và dtype được khai báo;
- cột toàn giá trị null và cột constant;
- bản ghi trùng và tên cột trùng;
- mixed dtype và chuỗi có cardinality cao;
- candidate ID;
- path không hợp lệ và format không được hỗ trợ;
- input DataFrame/configuration không hợp lệ;
- file hỏng và typed exception;
- JSON serialization;
- tính bất biến của file nguồn và DataFrame;
- các lần gọi lặp lại có tính deterministic;
- preview có giới hạn.

Fixture W01-T07 là các case DataFrame nhỏ trong bộ nhớ hoặc path tạm thời
trong tests/conftest.py. Không cần dataset thật hoặc dữ liệu nhạy cảm cho bằng
chứng này.

## Full Week 01 Regression

Lệnh regression đầy đủ của W01 đã collect 437 test và cho kết quả:

| Kết quả | Số lượng |
| --- | ---: |
| Passed | 435 |
| Skipped | 2 |
| Failed | 0 |
| Warnings | 4 |
| Runtime | 2.01s |

Hai case skip là các case portability có chủ đích của pandas được liệt kê bên
dưới. Không phát hiện regression trong các module W01 được đánh giá.

## Quality Gates

| Gate | Kết quả |
| --- | --- |
| Behavioral pytest | PASS — 362 passed, 2 skipped, 0 failed |
| Schema pytest | PASS — 21 passed, 0 skipped, 0 failed |
| Full W01 regression | PASS — 435 passed, 2 skipped, 0 failed |
| compileall | PASS |
| mypy | PASS — không có lỗi trong 20 source file |
| ruff | PASS — tất cả check đều passed |

## Known Portability Skips

Hai check bị skip không phải là lỗi implementation:

1. test_check_duplicates_rejects_unhashable_candidate_key_values — runtime
   pandas hiện tại hỗ trợ giá trị list trong duplicated(subset=...).
2. test_describe_categorical_rejects_unhashable_object_values_when_frequency_cannot_be_computed —
   runtime pandas hiện tại hỗ trợ value_counts() với input unhashable đại diện.

Các test này vẫn được giữ lại để behavior được thể hiện rõ giữa các version
pandas, nhưng không tạo false failure trên runtime đang hỗ trợ behavior đó.

## Known Runtime Warnings

Bốn warning đến từ
test_describe_numeric_output_does_not_expose_non_finite_statistics. Input có
chủ đích chứa +inf và -inf, vì vậy pandas/NumPy phát RuntimeWarning trong quá
trình reduction và tính quantile. Structured output cuối cùng vẫn normalize
giá trị statistic không hữu hạn thành None, và behavioral test vẫn pass.

## Known Limitations

- Loader chỉ hỗ trợ CSV, Excel và Parquet theo contract Week 01, đồng thời
  đọc dữ liệu vào memory; chưa có streaming cho file lớn.
- ID detection chỉ báo cáo candidate dựa trên evidence, không chứng minh đó là
  business identity.
- Quality operation có thể từ chối giá trị không được hỗ trợ hoặc unhashable
  bằng typed InvalidDatasetError, tùy operation và runtime pandas.
- Input numeric không hữu hạn được normalize thành None trong descriptive
  output, nhưng pandas hoặc NumPy vẫn có thể phát runtime warning khi tính
  statistic.
- Giá trị categorical được stringify trong descriptive output. Vì vậy các
  giá trị nguồn khác kiểu có thể dùng chung một nhãn sau serialization.
- Một số portability test với giá trị unhashable có thể skip khi runtime
  pandas hiện tại hỗ trợ operation thay vì raise exception.
- Descriptive tool chỉ báo cáo evidence. Tool không thực hiện cleaning, feature
  engineering hoặc modeling.
- File fingerprinting và toàn bộ tính năng orchestration nằm ngoài evaluation
  này.

## Evaluation Conclusion

Evidence layer của Week 01 pass toàn bộ behavioral test không bị skip đã thực
thi. Schema validation suite pass hoàn toàn, full W01 regression không có
failure, và các gate về typing, linting và compilation đều pass. Hai case
portability theo runtime pandas vẫn được skip có chủ đích, còn bốn warning đã
biết đến từ việc test edge case numeric không hữu hạn. Bằng chứng đủ để đánh
dấu W01-T08 hoàn thành và chuyển sang W01-T09; đây không phải claim rằng hệ
thống production-ready hoặc đúng với mọi dataset.

## Status

W01-T08: COMPLETE

READY FOR W01-T09

## Definition of Done

- [x] Loader W01-T03 được ghi nhận và đưa vào phạm vi evaluation.
- [x] Inspection W01-T04 được ghi nhận và đưa vào phạm vi evaluation.
- [x] Semantics quality và các exception path của W01-T05 được ghi nhận.
- [x] Convention descriptive và giới hạn của W01-T06 được ghi nhận.
- [x] Fixture và bằng chứng edge case của W01-T07 được ghi nhận.
- [x] Định nghĩa metric và các lệnh evaluation của W01-T08 được ghi nhận.
- [x] File nguồn và DataFrame được ghi nhận là input bất biến.
- [x] Fingerprinting W01-T09 vẫn nằm ngoài phạm vi.
