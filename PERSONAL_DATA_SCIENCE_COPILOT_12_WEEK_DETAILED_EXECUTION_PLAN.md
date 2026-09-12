# PERSONAL DATA SCIENCE COPILOT
## Kế hoạch thực thi chi tiết 12 tuần theo từng task

> **Tài liệu gốc:** `PERSONAL_DATA_SCIENCE_COPILOT_FINAL_12_WEEK_PLAN.md`
>
> **Vai trò của tài liệu này:** biến baseline 12 tuần thành lịch làm việc có thể thực thi và kiểm tra hằng tuần. Tài liệu này không thay thế baseline về tầm nhìn, kiến trúc và ranh giới Human-in-the-Loop; nó là checklist triển khai đi kèm.
>
> **Thời lượng mặc định:** 10–15 giờ/tuần, 6 ngày làm việc/tuần, mỗi ngày khoảng 1,5–2,5 giờ.
>
> **Nguyên tắc xuyên suốt:** làm tool đáng tin cậy trước, sau đó mới tích hợp LLM; mọi thay đổi dữ liệu quan trọng phải có phê duyệt của con người; mỗi capability (khả năng) mới phải đi cùng test và evaluation case (ca đánh giá).

---

# 1. CÁCH SỬ DỤNG PLAN

## 1.1 Trạng thái của task

Dùng bốn trạng thái sau:

```text
[ ] TODO        Chưa bắt đầu
[~] IN PROGRESS Đang thực hiện
[x] DONE        Đã đạt đầy đủ Definition of Done
[!] BLOCKED     Đang bị chặn và đã ghi rõ nguyên nhân
```

Không đánh dấu `[x]` chỉ vì đã viết xong code. Một task chỉ hoàn thành khi:

1. Code chạy được.
2. Test liên quan chạy qua.
3. Output đúng schema đã định nghĩa.
4. Không vi phạm ranh giới an toàn.
5. Có ghi chú ngắn trong `docs/dev_journal.md`.
6. Có commit nhỏ, nội dung rõ ràng.

## 1.2 Quy trình chuẩn cho mỗi task

```text
Đọc yêu cầu
   ↓
Viết acceptance criteria
   ↓
Thiết kế input/output schema
   ↓
Implement phần nhỏ nhất chạy được
   ↓
Unit test
   ↓
Integration test nếu có nhiều component
   ↓
Thêm evaluation case
   ↓
Cập nhật tài liệu
   ↓
Commit
```

## 1.3 Quy tắc quản lý phạm vi

- `P0 — Bắt buộc`: phải hoàn thành để tuần được coi là đạt.
- `P1 — Nên có`: thực hiện sau toàn bộ P0.
- `P2 — Stretch`: chỉ làm khi còn thời gian; không được làm chậm P0.
- Task chưa hoàn thành cuối tuần phải được đưa vào backlog, không tự động kéo toàn bộ timeline lùi lại.
- Nếu thiếu thời gian, cắt P2 trước, sau đó cắt P1; không cắt test an toàn, approval gate hoặc raw-data immutability.

## 1.4 Nhịp làm việc gợi ý trong tuần

| Ngày | Trọng tâm | Kết quả cuối ngày |
|---|---|---|
| Ngày 1 | Học lý thuyết vừa đủ + chốt thiết kế | Ghi chú thiết kế và acceptance criteria |
| Ngày 2 | Implement phần lõi 1 | Code nhỏ nhất chạy được |
| Ngày 3 | Implement phần lõi 2 | Capability chính hoạt động độc lập |
| Ngày 4 | Tích hợp | Luồng end-to-end đầu tiên chạy được |
| Ngày 5 | Test + evaluation | Có số liệu đánh giá và lỗi đã biết |
| Ngày 6 | Refactor + docs + demo | Code sạch, tài liệu cập nhật, có minh chứng |
| Ngày 7 | Nghỉ hoặc xử lý blocker nhẹ | Không thêm scope mới |

## 1.5 Các lệnh kiểm tra chuẩn

Điều chỉnh lệnh theo package manager thực tế của dự án, nhưng nên duy trì các kiểm tra tương đương:

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/safety -q
ruff check .
ruff format --check .
mypy src
```

Không bắt buộc bật `mypy` nghiêm ngặt ngay từ Tuần 1, nhưng public interface (giao diện public của module), schema và tool contract phải có type hint.

---

# 2. KẾT QUẢ CẦN CÓ SAU MỖI TUẦN

| Tuần | Increment chạy được | Gate bắt buộc |
|---|---|---|
| 1 | Bộ tool dữ liệu deterministic | Core unit tests pass; source data không bị sửa |
| 2 | Local LLM gọi được tool bằng structured output | Tool selection ≥ 90% mục tiêu; output hợp lệ ≥ 98% |
| 3 | Ba Agent Skills đầu tiên | Trigger/non-trigger accuracy ≥ 90% |
| 4 | Single Copilot + workflow + CLI V0 | Hoàn thành 20 task profiling/quality end-to-end |
| 5 | Data-quality report + approval gate | Mutation không approval = 0 |
| 6 | EDA + thống kê có kiểm tra giả định | Chọn đúng phương pháp trên controlled test set |
| 7 | Phân tích file/database bằng SQL an toàn | Unsafe SQL execution = 0 |
| 8 | Preprocessing/feature engineering có phê duyệt | Có thể tái tạo transform từ log + config |
| 9 | Baseline ML có con người kiểm soát | Chạy xong 1 classification và 1 regression case |
| 10 | Sandbox + file operation được giới hạn | Toàn bộ escape/disallowed tests bị chặn |
| 11 | Freight showcase + hai experiment time-boxed | Demo domain chạy end-to-end; có quyết định keep/drop experiment |
| 12 | Product được đánh giá và trình diễn | Critical safety metrics bằng 0; có đủ portfolio artifacts |

---

# 3. WEEK 1 — RELIABLE DATA TOOLS

## 3.1 Mục tiêu tuần

Xây dựng các hàm Data Science thuần, có input/output rõ ràng, chạy độc lập mà không cần LLM. Đây là nền móng của toàn bộ Copilot.

## 3.2 Kết quả nhìn thấy được cuối tuần

Người dùng có thể truyền một file CSV, Excel hoặc Parquet vào code và nhận được:

- shape;
- schema và dtype;
- preview;
- missing-value report;
- duplicate report;
- cardinality report;
- constant-column report;
- ID-candidate report;
- mô tả cột số và cột phân loại;
- lỗi có cấu trúc nếu file không hợp lệ.

## 3.3 Danh sách task

| ID | Priority | Task | Thời lượng | Phụ thuộc | Output chính |
|---|---:|---|---:|---|---|
| W01-T01 | P0 | Khởi tạo repository và môi trường | 1,5h | Không | Repo chạy được, dependency cố định |
| W01-T02 | P0 | Thiết kế tool contracts và schema chung | 1,5h | T01 | Pydantic result/error schemas |
| W01-T03 | P0 | Implement file loaders | 2h | T02 | CSV/Excel/Parquet loaders |
| W01-T04 | P0 | Implement inspection tools | 1,5h | T03 | Shape/schema/dtype/preview |
| W01-T05 | P0 | Implement quality tools cơ bản | 2,5h | T03 | Missing/duplicate/cardinality/constant/ID |
| W01-T06 | P0 | Implement descriptive tools | 1h | T03 | Numeric/categorical summaries |
| W01-T07 | P0 | Tạo fixtures và unit tests | 2,5h | T03–T06 | Bộ test edge cases |
| W01-T08 | P0 | Chạy evaluation và hoàn thiện tài liệu | 1h | T07 | Baseline metrics + dev journal |
| W01-T09 | P1 | Thêm file fingerprint | 0,5h | T03 | Hash/metadata để nhận diện dataset |

Tổng dự kiến: **13–14 giờ**.

## 3.4 Chi tiết từng task

### [ ] W01-T01 — Khởi tạo repository và môi trường

Thực hiện:

1. Tạo cấu trúc thư mục tối thiểu theo baseline.
2. Tạo `pyproject.toml` với Python 3.11+.
3. Thêm dependencies tối thiểu: `pandas`, `numpy`, `pyarrow`, `openpyxl`, `pydantic`, `pytest`.
4. Thêm development dependencies: `ruff`, `mypy` nếu phù hợp.
5. Tạo `.gitignore`; loại trừ `.env`, cache, model lớn, raw data thật và file tạm.
6. Tạo `README.md` bản skeleton và `docs/dev_journal.md`.
7. Chạy một smoke test import package.

Files:

```text
pyproject.toml
.gitignore
README.md
src/__init__.py
tests/
docs/dev_journal.md
```

Definition of Done:

- Cài môi trường mới không lỗi.
- `pytest` chạy được dù chưa có nhiều test.
- Import `src` hoặc package name thành công.
- Không commit dataset thật hoặc secrets.

### [ ] W01-T02 — Thiết kế tool contracts và schema chung

Thực hiện:

1. Định nghĩa nguyên tắc tool: deterministic, một trách nhiệm, không tự suy luận business meaning.
2. Tạo schema chung cho success, warning và error.
3. Thiết kế `DatasetReference`, `ToolError`, `ColumnSummary`, `MissingColumnResult`.
4. Chốt convention cho rate: số thực từ `0.0` đến `1.0`, không lưu dạng phần trăm string.
5. Chốt convention cho null, datetime, categorical và unsupported dtype.
6. Viết test validate schema và invalid input.

Files gợi ý:

```text
src/tools/schemas.py
src/tools/exceptions.py
tests/unit/test_tool_schemas.py
```

Definition of Done:

- Mỗi tool dự kiến đều có input/output contract.
- Schema từ chối dữ liệu sai kiểu.
- Error trả về mã lỗi, message an toàn và context cần thiết; không nuốt exception.

### [ ] W01-T03 — Implement file loaders

Thực hiện:

1. Viết `load_csv()`, `load_excel()`, `load_parquet()`.
2. Kiểm tra file tồn tại, extension, kích thước và sheet Excel.
3. Không sửa nội dung file nguồn.
4. Không tự đoán encoding vô hạn; hỗ trợ cấu hình encoding rõ ràng.
5. Với Excel, yêu cầu sheet hoặc áp dụng default được ghi rõ.
6. Chuẩn hóa metadata trả về: path, format, rows, columns, load warnings.

Test tối thiểu:

- file hợp lệ;
- file không tồn tại;
- extension không hỗ trợ;
- CSV rỗng;
- Excel nhiều sheet;
- Parquet hợp lệ;
- parse lỗi.

Definition of Done:

- Ba định dạng đều load được bằng cùng một abstraction.
- Lỗi đọc file có cấu trúc.
- Không phụ thuộc LLM.

### [ ] W01-T04 — Implement inspection tools

Implement:

```text
get_shape()
get_schema()
get_dtypes()
get_column_summary()
preview_data()
```

Yêu cầu:

- `preview_data()` giới hạn số hàng và số cột trả về.
- Schema giữ nguyên tên cột gốc nhưng phát cảnh báo cho tên trùng, tên rỗng hoặc tên khó dùng.
- Output JSON-serializable (có thể chuyển thành JSON).
- Không expose toàn bộ dữ liệu khi chỉ cần summary.

Definition of Done:

- Hoạt động với dataframe rỗng và dataframe có mixed dtype.
- Preview không vượt giới hạn cấu hình.
- Kết quả có Pydantic validation.

### [ ] W01-T05 — Implement quality tools cơ bản

Implement:

```text
check_missing()
check_duplicates()
check_cardinality()
check_constant_columns()
detect_id_candidates()
```

Yêu cầu quan trọng:

- `detect_id_candidates()` chỉ gắn nhãn **candidate**, không kết luận chắc chắn.
- Missing report phải chứa count, rate và severity rule minh bạch.
- Duplicate report tách full-row duplicate và khả năng trùng theo candidate key nếu được truyền vào.
- Cardinality phải tính cả unique count và unique rate.
- Không drop dòng hoặc cột.

Definition of Done:

- Kết quả đúng trên fixture có lỗi được cài sẵn.
- Severity không được hard-code rải rác; cấu hình hoặc helper dùng chung.
- Source dataframe trước và sau khi gọi tool giống nhau.

### [ ] W01-T06 — Implement descriptive tools

Implement:

```text
describe_numeric()
describe_categorical()
```

Numeric output tối thiểu:

```text
count, missing, mean, std, min, q1, median, q3, max
```

Categorical output tối thiểu:

```text
count, missing, unique, top_values, top_rates
```

Giới hạn số lượng top values để tránh output quá lớn.

### [ ] W01-T07 — Tạo fixtures và unit tests

Tạo dataset nhỏ có kiểm soát cho các tình huống:

```text
normal
empty
all_null_column
duplicate_rows
mixed_dtype
constant_column
high_cardinality_string
possible_id
invalid_path
unsupported_format
```

Thực hiện:

1. Mỗi tool có test happy path và ít nhất một edge case.
2. Thêm test immutability: hash/dataframe equality trước và sau khi chạy tool.
3. Thêm test JSON serialization.
4. Đặt tên test mô tả hành vi, không mô tả implementation.

Definition of Done:

- Core unit tests pass.
- Không có test phụ thuộc internet.
- Test chạy lặp lại cho cùng kết quả.

### [ ] W01-T08 — Evaluation và tài liệu

Ghi lại:

```text
tool_correctness
exception_correctness
schema_validation_rate
known_limitations
```

Cập nhật README:

- cách cài;
- cách chạy test;
- ví dụ gọi một loader và một quality tool;
- khẳng định raw data không bị sửa.

### [ ] W01-T09 — Thêm file fingerprint

Nếu còn thời gian, tạo fingerprint từ nội dung file hoặc tập metadata ổn định để nhận diện chính xác phiên bản dataset. Không dùng riêng filename làm định danh vì file cùng tên có thể đã thay đổi nội dung. Viết test chứng minh file không đổi cho cùng fingerprint và file thay đổi tạo fingerprint khác.

## 3.5 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 |
| 3 | T04 + bắt đầu T05 |
| 4 | Hoàn thành T05 + T06 |
| 5 | T07 |
| 6 | T08; T09 nếu còn thời gian |

## 3.6 Gate cuối tuần

- [ ] Ba loader hoạt động.
- [ ] Tất cả tool trả structured result.
- [ ] Có test cho toàn bộ edge cases bắt buộc.
- [ ] Không tool nào sửa source dataframe.
- [ ] Không có LLM trong business/data logic.

---

# 4. WEEK 2 — LOCAL LLM, STRUCTURED OUTPUT VÀ TOOL CALLING

## 4.1 Mục tiêu tuần

Cho local LLM hiểu yêu cầu người dùng, chọn đúng Week-1 tool, tạo arguments hợp lệ và trả lời dựa trên tool evidence (bằng chứng từ tool).

## 4.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W02-T01 | P0 | Cài Ollama và benchmark nhỏ | 1,5h | Model decision record |
| W02-T02 | P0 | Thiết kế `LLMProvider` abstraction | 1,5h | Provider interface |
| W02-T03 | P0 | Implement `OllamaProvider` | 1,5h | Local provider hoạt động |
| W02-T04 | P0 | Xây `ToolRegistry` | 1,5h | Registry có schema + permission metadata |
| W02-T05 | P0 | Xây `ToolExecutor` | 2h | Validate → execute → validate result |
| W02-T06 | P0 | Tạo tool-calling loop tối thiểu | 2h | Một vòng User → LLM → Tool → Response |
| W02-T07 | P0 | Tạo 30 golden prompts | 1,5h | Dataset đánh giá tool calling |
| W02-T08 | P0 | Chạy eval, sửa lỗi và ghi metrics | 1,5h | Báo cáo Week 2 |
| W02-T09 | P1 | Fallback khi structured output lỗi | 1h | Retry có giới hạn |

Tổng dự kiến: **13–14 giờ**.

## 4.3 Chi tiết task trọng yếu

### [ ] W02-T01 — Cài Ollama và benchmark nhỏ

Thực hiện:

1. Ghi cấu hình máy: RAM, VRAM nếu có, CPU, hệ điều hành.
2. Chọn tối đa 2–3 model có khả năng tool calling/structured output.
3. Dùng cùng 10 prompt nhỏ để so sánh.
4. Đo: JSON validity, tool choice, argument accuracy, latency.
5. Chọn một model mặc định; model name nằm trong config, không nằm trong business logic.

Output:

```text
docs/decisions.md
config/models.yaml
evals/results/week02_model_benchmark.*
```

Không dành quá 1,5 giờ cho việc thử model. Mục tiêu tuần là tool calling, không phải tìm model hoàn hảo.

### [ ] W02-T02 — Thiết kế `LLMProvider`

Interface tối thiểu:

```text
generate()
generate_structured()
generate_with_tools()
health_check()
```

Yêu cầu:

- Business logic không import trực tiếp SDK Ollama.
- Request/response có schema.
- Provider trả usage/latency nếu có.
- Timeout và lỗi kết nối được phân loại.

### [ ] W02-T03 — Implement `OllamaProvider`

Thực hiện:

1. Load endpoint/model từ config hoặc environment.
2. Implement health check.
3. Implement structured output theo JSON schema.
4. Implement tool declaration mapping.
5. Test provider bằng mock để test không phụ thuộc model đang chạy.
6. Thêm một integration test được đánh dấu riêng, chỉ chạy khi Ollama sẵn sàng.

### [ ] W02-T04 — Xây `ToolRegistry`

Mỗi tool entry cần:

```text
name
description
input_schema
output_schema
permission_class
callable_reference
version
```

Thực hiện:

- register tool;
- list allowed tools;
- lấy schema để gửi LLM;
- từ chối tool không đăng ký;
- phát hiện trùng tên.

### [ ] W02-T05 — Xây `ToolExecutor`

Flow bắt buộc:

```text
Nhận tool call
→ kiểm tra tool có đăng ký
→ validate arguments
→ kiểm tra permission class
→ execute trusted Python function
→ validate result
→ ghi execution summary
```

Test:

- đúng tool, đúng argument;
- tool không tồn tại;
- thiếu argument;
- sai kiểu;
- path ngoài project root;
- tool raise exception;
- output không đúng schema.

### [ ] W02-T06 — Tool-calling loop tối thiểu

Thực hiện:

1. Viết system instruction ngắn, chỉ mô tả vai trò và ranh giới.
2. Gửi danh sách tool từ registry.
3. Nhận tool call từ model.
4. Thực thi bằng executor.
5. Trả tool result lại model.
6. Buộc final answer phân biệt `finding`, `evidence`, `limitation`.
7. Giới hạn số vòng tool call.

Không cho phép:

- arbitrary Python;
- shell;
- automatic mutation;
- delete;
- truy cập file ngoài approved project root.

### [ ] W02-T07 — Tạo 30 golden prompts

Phân bổ gợi ý:

| Nhóm | Số prompt |
|---|---:|
| Load/inspect | 8 |
| Missing/duplicate | 6 |
| Cardinality/constant/ID | 6 |
| Numeric/categorical description | 6 |
| Invalid/ambiguous/out-of-scope | 4 |

Mỗi case lưu:

```text
prompt
dataset_ref
expected_tool
expected_arguments
allowed_alternatives
expected_safety_behavior
```

### [ ] W02-T08 — Evaluation

Tính:

```text
tool_selection_accuracy
argument_validity
execution_success
structured_output_validity
p50_latency
p95_latency
```

Mục tiêu:

- tool selection ≥ 90% nếu phần cứng/model đáp ứng;
- argument validity ≥ 95%;
- execution success ≥ 95%;
- structured output validity ≥ 98%.

Nếu chưa đạt, ghi rõ lỗi thuộc model, prompt, schema hay executor. Không sửa expected result để làm đẹp điểm.

### [ ] W02-T09 — Fallback khi structured output lỗi

Implement retry có giới hạn cho output không đúng schema:

1. Lần đầu gửi schema và instruction bình thường.
2. Nếu validation fail, trả validation errors ngắn gọn cho model và yêu cầu sửa đúng một lần.
3. Nếu vẫn lỗi, dừng an toàn và trả structured error; không cố parse bằng heuristic mơ hồ.

Ghi số lần retry vào run metadata để Week 12 đo reliability và latency.

## 4.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + thiết kế T02 |
| 2 | T02 + T03 |
| 3 | T04 |
| 4 | T05 + bắt đầu T06 |
| 5 | Hoàn thành T06 + T07 |
| 6 | T08; T09 nếu cần |

## 4.5 Gate cuối tuần

- [ ] LLM provider có thể thay thế.
- [ ] Model gọi được Week-1 tools.
- [ ] Arguments và outputs đều được validate.
- [ ] Có tối thiểu 30 golden prompts.
- [ ] Lỗi và giới hạn model được ghi trung thực.
- [ ] Không có Python/shell/mutation ngoài registry.

---

# 5. WEEK 3 — AGENT SKILLS

## 5.1 Mục tiêu tuần

Đưa kiến thức quy trình Data Science ra khỏi giant prompt (prompt khổng lồ), tổ chức thành các skill có trigger, evidence requirement, tool sequence và approval rule rõ ràng.

## 5.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W03-T01 | P0 | Học cấu trúc Agent Skills và chốt convention | 1,5h | Skill authoring guide |
| W03-T02 | P0 | Xây `SkillMetadata` và registry | 1,5h | Skill registry |
| W03-T03 | P0 | Xây skill loader + validator | 1,5h | Loader đọc `SKILL.md` |
| W03-T04 | P0 | Xây skill selector | 1,5h | Chọn skill từ intent |
| W03-T05 | P0 | Viết skill `data-profiling` | 1,5h | Skill 01 |
| W03-T06 | P0 | Viết skill `data-quality` | 1,5h | Skill 02 |
| W03-T07 | P0 | Viết skill `leakage-analysis` | 2h | Skill 03 |
| W03-T08 | P0 | Tạo 30 trigger/non-trigger tests | 1,5h | Skill eval set |
| W03-T09 | P0 | Đánh giá và chỉnh selector | 1h | Accuracy report |

Tổng dự kiến: **13,5 giờ**.

## 5.3 Chi tiết task

### [ ] W03-T01 — Chốt skill convention

Tạo tài liệu hướng dẫn để tất cả skill dùng cùng cấu trúc:

```text
name
purpose
when_to_use
when_not_to_use
required_context
required_evidence
tool_sequence
interpretation_rules
approval_rules
stop_conditions
expected_output
references
```

Quy tắc:

- Skill mô tả procedure/knowledge; không chứa calculation logic có thể viết thành tool.
- Skill không được tự cấp quyền cho chính nó.
- Skill không được thay thế approval policy.
- Chỉ load reference cần thiết để tránh context quá lớn.

### [ ] W03-T02 — `SkillMetadata` và registry

Implement:

```text
register_skill()
get_skill()
list_skills()
validate_unique_name()
```

Metadata cần version để sau này biết evaluation được chạy với bản skill nào.

### [ ] W03-T03 — Skill loader + validator

Thực hiện:

1. Tìm skill trong approved skill root.
2. Đọc `SKILL.md`.
3. Parse metadata.
4. Kiểm tra section bắt buộc.
5. Không đọc đường dẫn ra ngoài skill root.
6. Trả lỗi rõ ràng nếu skill invalid.

### [ ] W03-T04 — Skill selector

Thiết kế hai tầng:

```text
Rule/metadata pre-filter
        ↓
LLM chọn trong candidate skills nhỏ
```

Selector trả:

```text
selected_skill
confidence
reason_summary
required_clarification
```

Không cần chọn skill nếu yêu cầu chỉ là một phép tính deterministic đơn lẻ.

### [ ] W03-T05 — Skill `data-profiling`

Phải chỉ rõ:

- khi người dùng muốn hiểu cấu trúc dataset;
- tool sequence chuẩn;
- giới hạn preview;
- không diễn giải business meaning khi chưa có context;
- output gồm overview, schema, summaries và warnings.

### [ ] W03-T06 — Skill `data-quality`

Phải phân biệt:

```text
detect issue
recommend treatment
execute treatment
```

Tuần 3 mới tập trung detect và report; mutation chưa được chạy.

### [ ] W03-T07 — Skill `leakage-analysis`

Skill phải buộc Copilot hỏi hoặc xác nhận:

1. Target là gì?
2. Prediction moment (thời điểm đưa ra dự đoán) là khi nào?
3. Cột này có tồn tại tại prediction moment không?
4. Cột có được tạo từ outcome/target không?
5. Cột có chứa thông tin tương lai không?

Output không được kết luận chắc chắn nếu thiếu business context. Dùng các mức `low`, `medium`, `high`, `unknown` kèm lý do và câu hỏi cho con người.

### [ ] W03-T08 — Trigger/non-trigger tests

Tạo tối thiểu:

- 10 prompt cho profiling;
- 10 prompt cho data quality;
- 10 prompt cho leakage;
- trong mỗi nhóm có câu nên trigger và không nên trigger;
- thêm câu mơ hồ, tiếng Việt, tiếng Anh và câu trộn hai ngôn ngữ.

### [ ] W03-T09 — Đánh giá selector

Ghi confusion cases:

- profiling bị nhầm với quality;
- quality bị nhầm với preprocessing;
- leakage bị nhầm với feature importance;
- yêu cầu out-of-scope vẫn chọn skill.

Mục tiêu selection accuracy ≥ 90%.

## 5.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 + T04 |
| 3 | T05 |
| 4 | T06 |
| 5 | T07 |
| 6 | T08 + T09 |

## 5.5 Gate cuối tuần

- [ ] Có đúng ba production-quality skills đầu tiên.
- [ ] Skill loader từ chối skill sai cấu trúc hoặc path không an toàn.
- [ ] Skill selector đạt mục tiêu hoặc có limitation report.
- [ ] Leakage skill không thay con người kết luận business leakage.
- [ ] DS logic quan trọng không chỉ nằm trong system prompt.

---

# 6. WEEK 4 — SINGLE COPILOT, ROUTING, WORKFLOWS VÀ CLI

## 6.1 Mục tiêu tuần

Ghép tools, skills, LLM và state thành một Copilot duy nhất có khả năng tự route yêu cầu vào direct tool hoặc deterministic workflow.

## 6.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W04-T01 | P0 | Thiết kế orchestrator contract | 1,5h | Orchestrator input/output schema |
| W04-T02 | P0 | Implement router policy | 1,5h | Direct tool/workflow/reasoning routing |
| W04-T03 | P0 | Implement session state | 1,5h | State trong current run |
| W04-T04 | P0 | Implement profiling workflow | 1,5h | Workflow deterministic 01 |
| W04-T05 | P0 | Implement data-quality workflow cơ bản | 2h | Workflow deterministic 02 |
| W04-T06 | P0 | Implement stop/retry/error policy | 1h | Boundaries chống loop |
| W04-T07 | P0 | Xây CLI V0 | 2h | `inspect`, `quality`, `chat` |
| W04-T08 | P0 | Integration tests + 20 E2E tasks | 2h | Báo cáo Milestone B |
| W04-T09 | P1 | Response builder thống nhất | 1h | Finding/Evidence/Next step |

Tổng dự kiến: **13–14 giờ**.

## 6.3 Chi tiết task

### [ ] W04-T01 — Orchestrator contract

Input tối thiểu:

```text
user_request
session_id
dataset_reference_if_any
current_state
```

Output tối thiểu:

```text
status
selected_route
selected_skill
selected_workflow
findings
evidence
warnings
approval_request
artifacts
state_update
```

Orchestrator điều phối, không chứa trực tiếp code tính missing, SQL hay train model.

### [ ] W04-T02 — Router policy

Implement ba route:

| Loại yêu cầu | Route |
|---|---|
| Một phép tính rõ ràng | Direct tool |
| Quy trình đã biết nhiều bước | Deterministic workflow |
| Cần giải thích/lựa chọn mở | LLM reasoning dựa trên evidence |

Router phải có route `clarify` khi thiếu dataset, target hoặc câu hỏi quá mơ hồ.

Test ít nhất:

- “Cho tôi schema” → direct tool;
- “Kiểm tra chất lượng dữ liệu” → workflow;
- “Có nên bỏ cột này không?” → evidence + recommendation;
- “Phân tích đi” khi chưa có file → clarify.

### [ ] W04-T03 — Session state

Track:

```text
active_dataset
dataset_fingerprint
schema
target_if_known
completed_workflows
warnings
current_task
tool_history
```

Không triển khai persistent memory phức tạp. State chỉ cần sống trong current run.

### [ ] W04-T04 — Profiling workflow

Thứ tự cố định:

```text
load
→ shape
→ schema/dtypes
→ preview
→ numeric/categorical description
→ assemble report
```

Yêu cầu:

- một step lỗi không làm mất toàn bộ context;
- lỗi critical ở load thì dừng;
- mỗi step lưu structured result;
- rerun với cùng input cho kết quả tương đương.

### [ ] W04-T05 — Data-quality workflow cơ bản

Thứ tự:

```text
load
→ schema
→ missing
→ duplicate
→ cardinality
→ constants
→ ID candidates
→ report
```

Chưa tự động drop/impute.

### [ ] W04-T06 — Stop/retry/error policy

Cấu hình:

```text
max_workflow_steps
max_llm_calls
max_tool_retries
request_timeout
error_budget
```

Retry chỉ áp dụng lỗi có khả năng tạm thời hoặc structured output invalid; không retry vô hạn với cùng input.

### [ ] W04-T07 — CLI V0

Commands:

```bash
ds-copilot inspect data.csv
ds-copilot quality data.xlsx
ds-copilot chat
```

CLI phải:

- hiện progress ngắn;
- phân biệt finding, evidence, warning;
- trả exit code khác 0 khi lỗi;
- không in traceback dài cho user mặc định;
- có `--verbose` cho developer.

### [ ] W04-T08 — 20 end-to-end tasks

Phân bổ:

- 8 profiling;
- 8 data-quality;
- 2 clarification;
- 2 invalid/safety.

Đo:

```text
routing_accuracy
workflow_completion_rate
task_success_rate
average_llm_calls
average_tool_calls
```

### [ ] W04-T09 — Response builder thống nhất

Nếu còn thời gian, gom cách dựng câu trả lời vào một component dùng chung. Output tối thiểu gồm `Finding`, `Evidence`, `Warning/Limitations`, `Recommendation` và `Human Decision Required` khi phù hợp. Response builder chỉ trình bày result; không được tự thay đổi quyết định từ workflow hoặc permission policy.

## 6.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 + T04 |
| 3 | T05 |
| 4 | T06 + T07 |
| 5 | Hoàn thiện CLI + integration tests |
| 6 | T08 + T09 + milestone review |

## 6.5 Gate cuối tuần

- [ ] Chỉ có một orchestrator.
- [ ] Direct tool và workflow được route đúng.
- [ ] Có stop policy; không loop vô hạn.
- [ ] CLI chạy được trên ít nhất CSV và Excel.
- [ ] Hoàn thành 20 E2E tasks với failure analysis.

---

# 7. WEEK 5 — DATA QUALITY, LEAKAGE VÀ APPROVAL SYSTEM

## 7.1 Mục tiêu tuần

Mở rộng kiểm tra dữ liệu trước modeling và thiết lập ranh giới kỹ thuật bắt buộc giữa read-only, recommendation và mutation.

## 7.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W05-T01 | P0 | Thiết kế permission classes | 1h | READ_ONLY/RECOMMENDATION/MUTATION |
| W05-T02 | P0 | Xây `ApprovalRequest` schema | 1h | Approval contract |
| W05-T03 | P0 | Implement approval policy + audit log | 1,5h | Policy enforcement |
| W05-T04 | P0 | Implement outlier/skewness/low variance | 2h | Quality tools nâng cao 1 |
| W05-T05 | P0 | Implement invalid range/date/imbalance | 2h | Quality tools nâng cao 2 |
| W05-T06 | P0 | Implement leakage-candidate detector | 2h | Evidence-based warnings |
| W05-T07 | P0 | Hoàn thiện Data Quality Report | 1,5h | Report tổng hợp |
| W05-T08 | P0 | Tạo synthetic validation dataset | 1h | Controlled anomalies |
| W05-T09 | P0 | Safety/integration evaluation | 1,5h | Mutation-without-approval = 0 |

Tổng dự kiến: **13,5 giờ**.

## 7.3 Chi tiết task

### [ ] W05-T01 — Permission classes

Chốt mapping:

```text
READ_ONLY       đọc, tính toán, vẽ, xem metrics
RECOMMENDATION  đề xuất; cần human review
MUTATION        thay đổi dữ liệu/file/model artifact; cần explicit approval
```

Permission class là metadata của tool/action, không do LLM tự sinh để tự cấp quyền.

### [ ] W05-T02 — `ApprovalRequest`

Schema bắt buộc:

```text
approval_id
action
reason
evidence
affected_data
expected_effect
risk
reversible
proposed_output
expires_at_or_scope
```

Human response:

```text
approved
rejected
modified
decision_note
```

Approval chỉ hợp lệ cho đúng action, đúng dataset fingerprint và đúng parameters đã hiển thị.

### [ ] W05-T03 — Approval policy và audit

Flow:

```text
Action request
→ permission lookup
→ nếu READ_ONLY: execute
→ nếu RECOMMENDATION: return recommendation
→ nếu MUTATION: create approval request và stop
→ human decision
→ verify scope
→ execute nếu approved
→ log decision
```

Test critical:

- forged approval ID;
- approval cho dataset A dùng với dataset B;
- thay argument sau approval;
- reuse approval đã hết hiệu lực;
- rejection vẫn bị execute;
- tool thiếu permission metadata.

Tất cả phải bị chặn an toàn.

### [ ] W05-T04 — Outlier, skewness, low variance

Implement:

```text
detect_outliers()
detect_skewness()
detect_low_variance()
```

Yêu cầu:

- Outlier method được nêu rõ: IQR, z-score hoặc method phù hợp.
- Không tự xóa outlier.
- Skewness là bằng chứng mô tả, không tự động log-transform.
- Low variance threshold cấu hình được.

### [ ] W05-T05 — Invalid range, date và imbalance

Implement:

```text
detect_invalid_ranges()
detect_date_columns()
detect_class_imbalance()
detect_possible_ids()
```

`detect_invalid_ranges()` cần rule do người dùng/config cung cấp; Copilot không tự coi tuổi 120 hay cost âm là invalid nếu chưa có rule/domain context, nhưng có thể gắn cờ bất thường.

### [ ] W05-T06 — Leakage-candidate detector

Sử dụng nhiều tín hiệu nhưng chỉ tạo candidate:

- tên cột giống target/outcome;
- feature là phép biến đổi trực tiếp của target;
- timestamp sau prediction moment nếu context có sẵn;
- near-perfect association;
- cột status/result chỉ có sau outcome;
- duplicated target encoding.

Mỗi result phải có:

```text
column
risk_level
reason
evidence
availability_at_prediction_time
questions_for_human
recommendation
human_confirmation_required
```

### [ ] W05-T07 — Data Quality Report

Sections:

```text
Dataset Overview
Schema
Missing
Duplicates
Cardinality
Constants
IDs
Outliers
Skewness
Target
Class Balance
Leakage Candidates
Risks
Recommended Actions
```

Mỗi recommendation phải trỏ về evidence ID hoặc tool result tương ứng.

### [ ] W05-T08 — Synthetic validation dataset

Cài có chủ đích:

```text
missing
duplicate
constant
outlier
ID
wrong dtype
imbalance
post-outcome leakage
target-derived feature
```

Lưu expected findings tách biệt với detector output để tránh self-confirming test.

### [ ] W05-T09 — Safety/integration evaluation

Mục tiêu critical:

```text
mutation_without_approval = 0
raw_source_modified = 0
approval_scope_mismatch_executed = 0
```

## 7.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01–T03 |
| 2 | T04 |
| 3 | T05 |
| 4 | T06 |
| 5 | T07 + T08 |
| 6 | T09 + milestone review |

## 7.5 Gate cuối tuần

- [ ] Mọi action có permission class.
- [ ] Mutation thiếu approval bị chặn ở code, không chỉ ở prompt.
- [ ] Leakage output là candidate + evidence, không phải phán quyết.
- [ ] Synthetic dataset được detector tìm đúng các lỗi đã biết.
- [ ] Source dataset không bị sửa.

---

# 8. WEEK 6 — EDA, VISUALIZATION VÀ STATISTICS

## 8.1 Mục tiêu tuần

Tự động hóa phần EDA cơ học và phép kiểm định phổ biến, đồng thời buộc Copilot kiểm tra loại biến, assumptions (giả định) và giới hạn diễn giải.

## 8.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W06-T01 | P0 | Thiết kế plot và statistical result schemas | 1h | Output contracts |
| W06-T02 | P0 | Implement distribution plots | 1,5h | Histogram/box/bar/target |
| W06-T03 | P0 | Implement relationship plots | 1,5h | Scatter/correlation/missingness |
| W06-T04 | P0 | Implement correlation + normality | 1,5h | Pearson/Spearman/normality |
| W06-T05 | P0 | Implement hypothesis tests + effect size | 2,5h | Chi-square/t/MW/ANOVA/effect size |
| W06-T06 | P0 | Xây method-selection rules | 1,5h | Chọn method dựa trên variable types |
| W06-T07 | P0 | Viết EDA và statistical-analysis skills | 1,5h | Hai skills |
| W06-T08 | P0 | Xây workflows + artifact saving | 1,5h | EDA/stat workflow |
| W06-T09 | P0 | Controlled evaluation set | 1,5h | Calculation/method eval |

Tổng dự kiến: **14 giờ**.

## 8.3 Chi tiết task

### [ ] W06-T01 — Output schemas

Plot result:

```text
plot_type
columns
filters
artifact_path
data_summary
warnings
```

Statistical result:

```text
question
method
why_this_method
assumptions
assumption_checks
statistic
p_value
effect_size
evidence
interpretation
limitations
```

### [ ] W06-T02 — Distribution plots

Implement:

```text
plot_histogram()
plot_boxplot()
plot_bar()
plot_target_distribution()
```

Yêu cầu:

- giới hạn categories;
- xử lý missing rõ ràng;
- title/axis label có nghĩa;
- plot path nằm trong `artifacts/plots`;
- không nhúng hàng triệu điểm vào chart.

### [ ] W06-T03 — Relationship plots

Implement:

```text
plot_scatter()
plot_correlation()
plot_missingness()
```

Thêm sampling deterministic nếu dữ liệu quá lớn và ghi sampling rate vào result.

### [ ] W06-T04 — Correlation và normality

Implement:

```text
pearson()
spearman()
normality_summary()
```

Không biến normality thành một nút yes/no đơn giản. Báo sample size, method, statistic và lưu ý kiểm định có thể quá nhạy khi n lớn.

### [ ] W06-T05 — Hypothesis tests và effect size

Implement:

```text
chi_square()
t_test()
mann_whitney()
anova()
effect_size()
```

Mỗi function:

- kiểm tra input type;
- kiểm tra số nhóm và sample size;
- trả assumptions;
- trả effect size khi có thể;
- không diễn giải causality;
- không chỉ dựa vào p-value.

### [ ] W06-T06 — Method-selection rules

Ví dụ mapping:

| Câu hỏi/biến | Candidate method | Điều kiện cần kiểm tra |
|---|---|---|
| Numeric–numeric | Pearson/Spearman | tuyến tính, outlier, phân phối |
| Categorical–categorical | Chi-square | expected cell count |
| Numeric giữa 2 nhóm | t-test/Mann–Whitney | độc lập, phân phối, variance |
| Numeric giữa >2 nhóm | ANOVA hoặc alternative | independence, residual assumptions |

LLM có thể giải thích, nhưng rule và validation phải nằm trong code/workflow.

### [ ] W06-T07 — Skills

`eda` skill cần nhấn mạnh:

- câu hỏi phân tích trước chart;
- chọn chart theo loại biến;
- không tạo chart vô mục đích;
- nêu missing/filter/sampling.

`statistical-analysis` skill cần nhấn mạnh:

- giả thuyết;
- assumptions;
- effect size;
- statistical vs practical significance;
- correlation không đồng nghĩa causation.

### [ ] W06-T08 — Workflows

Flow:

```text
Question
→ inspect variable types
→ choose valid method
→ check assumptions
→ execute
→ generate evidence
→ conservative interpretation
→ limitations
```

### [ ] W06-T09 — Controlled evaluation

Tạo dữ liệu có quan hệ biết trước:

- correlated numeric pair;
- monotonic non-linear pair;
- independent variables;
- two groups có/không có difference;
- categorical association;
- assumption violation;
- insufficient sample.

Đánh giá hai lớp tách biệt:

1. Calculation correctness.
2. Method-selection correctness.

## 8.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 + T04 |
| 3 | T05 phần 1 |
| 4 | T05 phần 2 + T06 |
| 5 | T07 + T08 |
| 6 | T09 + milestone review |

## 8.5 Gate cuối tuần

- [ ] Plot tools lưu artifact và metadata.
- [ ] Statistical tools kiểm tra input/assumptions.
- [ ] Interpretation có effect size/limitation khi phù hợp.
- [ ] Không có câu kết luận correlation = causation.
- [ ] Controlled test set cho kết quả mong đợi.

---

# 9. WEEK 7 — SAFE SQL VÀ FILE/DATABASE UNIFICATION

## 9.1 Mục tiêu tuần

Dùng DuckDB làm lớp phân tích SQL thống nhất cho file và local database, hỗ trợ Natural Language to SQL (chuyển câu hỏi tự nhiên thành SQL) nhưng chặn mọi lệnh ghi.

## 9.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W07-T01 | P0 | Thiết kế SQL connection/catalog abstraction | 1,5h | DuckDB session layer |
| W07-T02 | P0 | Implement schema inspection tools | 1,5h | list/schema/preview/describe |
| W07-T03 | P0 | Implement static SQL validator | 2h | Allowlist SELECT/WITH/EXPLAIN |
| W07-T04 | P0 | Implement read-only executor | 1,5h | Bounded query execution |
| W07-T05 | P0 | Xây NL2SQL workflow | 2h | Schema-grounded SQL generation |
| W07-T06 | P0 | Viết `sql-analysis` skill | 1h | Skill + safety rules |
| W07-T07 | P0 | Tạo 40 SQL evaluation tasks | 2h | Golden SQL dataset |
| W07-T08 | P0 | Freight KPI query pack | 1h | 5+ business queries |
| W07-T09 | P0 | Chạy correctness + safety eval | 1,5h | Unsafe execution = 0 |

Tổng dự kiến: **14 giờ**.

## 9.3 Chi tiết task

### [ ] W07-T01 — DuckDB session/catalog layer

Hỗ trợ:

- CSV;
- Parquet;
- Excel sau khi được load/convert thành relation phù hợp;
- DuckDB file local.

Track table name, source, schema và dataset fingerprint. Không tự động attach nguồn ngoài approved project root.

### [ ] W07-T02 — Schema inspection tools

Implement:

```text
list_tables()
get_table_schema()
preview_table()
describe_table()
```

Preview có row limit. Table/column identifiers phải được quote/validate đúng cách.

### [ ] W07-T03 — Static SQL validator

Allow:

```text
SELECT
WITH
EXPLAIN
```

Block ít nhất:

```text
INSERT UPDATE DELETE DROP ALTER TRUNCATE CREATE
COPY EXPORT IMPORT INSTALL LOAD
ATTACH DETACH
PRAGMA nguy hiểm
nhiều statement trong một request
```

Không dùng regex đơn giản làm lớp bảo vệ duy nhất. Dùng parser/AST nếu phù hợp và defense-in-depth (nhiều lớp bảo vệ).

Test:

- keyword viết hoa/thường;
- comment chen giữa keyword;
- multiple statements;
- CTE chứa lệnh không an toàn;
- tên cột giống từ khóa;
- quoted strings có từ `DROP` nhưng query vẫn an toàn;
- obfuscated unsafe prompt.

### [ ] W07-T04 — Read-only executor

Giới hạn:

```text
row_limit
timeout
memory_limit_if_supported
result_size_limit
approved_connection
```

Executor chỉ chạy sau khi validator pass. Connection cũng phải được cấu hình read-only khi backend hỗ trợ.

### [ ] W07-T05 — NL2SQL workflow

Flow:

```text
Business question
→ inspect schema
→ identify relevant tables/columns
→ clarify if ambiguous
→ generate SQL
→ static validation
→ optional EXPLAIN
→ execute
→ validate result shape
→ explain with evidence
```

LLM không được invent column (bịa tên cột). Nếu schema không có dữ liệu cần thiết, trả limitation.

### [ ] W07-T06 — SQL skill

Skill phải yêu cầu:

- schema grounding;
- use business definition cho KPI;
- explicit filters/date range;
- safe read-only query;
- explanation gắn với result;
- không khẳng định nguyên nhân từ aggregate đơn thuần.

### [ ] W07-T07 — 40 evaluation tasks

Phân bổ gợi ý:

| Nhóm | Số task |
|---|---:|
| Filter/sort/top-N | 7 |
| Group-by/aggregation | 8 |
| Date aggregation | 5 |
| Join | 5 |
| CTE/window | 5 |
| Invalid/ambiguous schema | 5 |
| Unsafe/adversarial | 5 |

Mỗi task có expected columns, expected row count hoặc result checksum; không chỉ so exact SQL string vì nhiều query tương đương có thể đúng.

### [ ] W07-T08 — Freight KPI query pack

Tạo query cho:

```text
top routes by shipment count
average delay by carrier
on-time rate by month
cost per shipment by route
worst lanes by delay
```

Ghi rõ denominator và rule xử lý missing cho từng KPI.

### [ ] W07-T09 — Evaluation

Đo:

```text
SQL_execution_accuracy
result_correctness
schema_grounding_rate
unsafe_SQL_generation_rate
unsafe_SQL_execution_rate
```

Critical: `unsafe_SQL_execution_rate = 0`.

## 9.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 |
| 3 | T04 + T05 phần 1 |
| 4 | T05 phần 2 + T06 |
| 5 | T07 + T08 |
| 6 | T09 + sửa failure cases |

## 9.5 Gate cuối tuần

- [ ] File và DuckDB dùng chung workflow.
- [ ] SQL validator và read-only connection đều được áp dụng.
- [ ] 40 evaluation tasks có expected result.
- [ ] Column hallucination được phát hiện hoặc từ chối.
- [ ] Unsafe SQL execution bằng 0.

---

# 10. WEEK 8 — PREPROCESSING VÀ FEATURE ENGINEERING

## 10.1 Mục tiêu tuần

Copilot phát hiện vấn đề/cơ hội, tạo proposal, chờ phê duyệt, thực hiện trên bản sao, kiểm tra before/after và ghi decision log để có thể tái tạo.

## 10.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W08-T01 | P0 | Thiết kế transformation proposal/config | 1,5h | Reproducible config schema |
| W08-T02 | P0 | Missing strategy + imputation | 2h | Propose/apply imputation |
| W08-T03 | P0 | Encoding + scaling + dtype/date | 2h | Preprocessing tools |
| W08-T04 | P0 | Feature tools có thể giải thích | 2h | Date/ratio/log/group/interaction |
| W08-T05 | P0 | Approval-aware preprocessing workflow | 2h | Proposal → approve → copy |
| W08-T06 | P0 | Before/after validation + decision log | 1,5h | Validation report |
| W08-T07 | P0 | Viết hai skills | 1h | Preprocessing/feature skills |
| W08-T08 | P0 | Reproducibility + safety tests | 1,5h | Replay transform tests |
| W08-T09 | P1 | Generate reusable pipeline config | 1h | Pipeline YAML/JSON |

Tổng dự kiến: **13,5–14,5 giờ**.

## 10.3 Chi tiết task

### [ ] W08-T01 — Transformation proposal/config

Schema:

```text
proposal_id
dataset_fingerprint
operation
columns
parameters
reason
evidence
expected_effect
risks
output_path
requires_approval
```

Config đã approve phải immutable; nếu đổi parameters thì tạo approval mới.

### [ ] W08-T02 — Missing strategy và imputation

Implement:

```text
propose_missing_strategy()
apply_imputation()
```

Proposal có thể gợi ý nhưng không tự quyết định:

- drop;
- mean/median/mode;
- constant;
- group-based;
- leave missing + indicator.

Khi apply:

- fit statistics chỉ trên training data trong ML context;
- không leakage từ validation/test;
- lưu learned values;
- tạo output copy.

### [ ] W08-T03 — Encoding, scaling, dtype/date

Implement:

```text
encode_one_hot()
encode_ordinal()
scale_standard()
scale_robust()
parse_dates()
cast_dtype()
```

Critical:

- ordinal encoding cần thứ tự do con người/config xác nhận;
- unknown category có policy;
- scaler lưu parameters;
- dtype conversion ghi số giá trị parse fail.

### [ ] W08-T04 — Feature tools có thể giải thích

Implement:

```text
create_date_parts()
create_ratio_feature()
create_log_transform()
create_group_aggregate()
create_interaction_candidate()
```

Mỗi feature lưu:

```text
source_columns
formula
business_rationale
availability_at_prediction_time
null_behavior
```

Group aggregate phải kiểm tra nguy cơ target leakage và train/test leakage.

### [ ] W08-T05 — Approval-aware workflow

Flow bắt buộc:

```text
Inspect
→ identify issue/opportunity
→ generate proposal
→ show evidence
→ STOP for human approval
→ verify approval scope
→ create transformed copy
→ validate
→ compare before/after
→ log decision
```

Raw data luôn nằm trong `data/raw` và chỉ đọc. Output đi vào `data/interim` hoặc `data/processed`.

### [ ] W08-T06 — Before/after validation

Báo cáo tối thiểu:

```text
row_count_before_after
column_count_before_after
dtype_changes
missing_before_after
new_columns
removed_columns
unexpected_value_changes
dataset_fingerprint_before_after
```

Nếu validation fail, không đánh dấu artifact là valid.

### [ ] W08-T07 — Skills

`preprocessing` skill mô tả cách chọn proposal dựa trên model/context, nhưng yêu cầu con người xác nhận strategy.

`feature-engineering` skill ưu tiên feature có ý nghĩa, sẵn có tại prediction time và dễ giải thích; không tạo hàng trăm tổ hợp vô kiểm soát.

### [ ] W08-T08 — Reproducibility và safety tests

Test:

- cùng raw fingerprint + cùng approved config → cùng output;
- khác raw fingerprint → approval cũ không dùng được;
- sửa config sau approval → bị chặn;
- raw file trước/sau giống nhau;
- rejected proposal không tạo processed file;
- replay decision log tái tạo được output.

### [ ] W08-T09 — Generate reusable pipeline config

Nếu còn thời gian, serialize toàn bộ preprocessing/feature steps đã được approve thành YAML hoặc JSON có version. Config phải tham chiếu dataset fingerprint, thứ tự step, parameters và fitted-artifact references; không lưu object Python không kiểm soát. Thử load lại config trong một process mới và tái tạo cùng output checksum.

## 10.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 phần proposal |
| 2 | Hoàn thành T02 + T03 phần 1 |
| 3 | Hoàn thành T03 + T04 |
| 4 | T05 |
| 5 | T06 + T07 |
| 6 | T08; T09 nếu còn thời gian |

## 10.5 Gate cuối tuần

- [ ] Mọi transform là mutation và cần approval.
- [ ] Raw data chưa từng bị overwrite.
- [ ] Output copy có fingerprint và lineage.
- [ ] Before/after validation report được tạo.
- [ ] Có thể replay transform từ decision log + config.

---

# 11. WEEK 9 — HUMAN-CONTROLLED BASELINE MACHINE LEARNING

## 11.1 Mục tiêu tuần

Tự động hóa phần cơ học của baseline experiment sau khi Data Scientist đã xác nhận target, prediction moment, problem type, split, metric, features và model candidates.

## 11.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W09-T01 | P0 | Thiết kế ML decision checklist + schemas | 1,5h | Required human decisions |
| W09-T02 | P0 | Problem-type, metric và split recommender | 1,5h | Evidence-based proposal |
| W09-T03 | P0 | Xây preprocessing/model pipeline | 2h | Leakage-safe sklearn pipeline |
| W09-T04 | P0 | Implement baseline trainers | 2h | Dummy + linear/tree candidates |
| W09-T05 | P0 | Implement evaluation + comparison | 2h | Metrics + dummy comparison |
| W09-T06 | P0 | Experiment registry và artifact metadata | 1,5h | Reproducible experiment record |
| W09-T07 | P0 | Error analysis cơ bản | 1h | Slice/error samples |
| W09-T08 | P0 | Viết modeling/evaluation skills + workflow | 1,5h | Controlled ML workflow |
| W09-T09 | P0 | Classification và regression E2E tests | 1,5h | Milestone D evidence |

Tổng dự kiến: **14,5 giờ**.

## 11.3 Chi tiết task

### [ ] W09-T01 — ML decision checklist

Human phải xác nhận:

```text
business_objective
target
prediction_moment
problem_type
main_metric
split_strategy
feature_set
approved_models
```

Copilot không cho train nếu thiếu target, prediction moment, leakage review, split hoặc metric chính.

### [ ] W09-T02 — Recommenders

Copilot có thể đề xuất:

- classification/regression;
- metric candidates;
- random/time/group split;
- model candidates.

Nhưng output phải bao gồm evidence và trade-off. Ví dụ không tự chọn accuracy khi class imbalance nghiêm trọng.

### [ ] W09-T03 — Leakage-safe pipeline

Yêu cầu:

- split trước khi fit preprocessing;
- imputer/encoder/scaler fit trên train;
- cùng fitted pipeline transform validation/test;
- random seed được lưu;
- feature names sau transform được track;
- không đọc target trong feature transformer.

### [ ] W09-T04 — Baseline trainers

Classification candidates:

```text
DummyClassifier
LogisticRegression
RandomForestClassifier
XGBoostClassifier nếu dependency ổn định
```

Regression candidates:

```text
DummyRegressor
LinearRegression
RandomForestRegressor
XGBoostRegressor nếu dependency ổn định
```

Không chạy tất cả tự động. Chỉ chạy approved model list và time-box hyperparameters đơn giản; V1 không phải AutoML.

### [ ] W09-T05 — Evaluation và comparison

Classification hỗ trợ candidate metrics:

```text
accuracy
precision
recall
f1
roc_auc
pr_auc
confusion_matrix
```

Regression:

```text
MAE
RMSE
R2
```

Luôn so với dummy baseline. Report nêu rõ main metric do human xác nhận và secondary metrics để cung cấp context.

### [ ] W09-T06 — Experiment registry

Store:

```text
experiment_id
dataset_fingerprint
target
features
split
preprocessing
model
hyperparameters
metrics
timestamp
decision_references
artifact_paths
code_version_if_available
```

Không cần MLflow ở V1; JSON/SQLite/local files có cấu trúc là đủ.

### [ ] W09-T07 — Error analysis

Tối thiểu:

- false positive/false negative samples cho classification;
- largest residuals cho regression;
- metric theo một vài slice được human chọn;
- không expose toàn bộ sensitive rows trong report mặc định.

### [ ] W09-T08 — Skills và workflow

Workflow:

```text
confirmed target
→ problem recommendation
→ leakage review
→ split recommendation
→ metric recommendation
→ HUMAN APPROVAL
→ build pipeline
→ train approved baselines
→ evaluate
→ compare with dummy
→ error analysis
→ recommendation
```

### [ ] W09-T09 — Hai E2E cases

Case A — classification:

- target nhị phân;
- có imbalance nhẹ;
- có categorical + numeric;
- có missing;
- so với DummyClassifier.

Case B — regression:

- target liên tục;
- có skewed feature;
- có missing;
- so với DummyRegressor.

Kiểm tra cả happy path và “train ngay đi” khi chưa đủ human decisions; trường hợp thứ hai phải dừng và hỏi xác nhận.

## 11.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 |
| 3 | T04 |
| 4 | T05 + T06 |
| 5 | T07 + T08 |
| 6 | T09 + milestone review |

## 11.5 Gate cuối tuần

- [ ] Không train khi thiếu quyết định bắt buộc.
- [ ] Preprocessing được fit chỉ trên train.
- [ ] Mọi model được so với dummy baseline.
- [ ] Experiment có đầy đủ metadata và artifact paths.
- [ ] Classification và regression controlled cases chạy end-to-end.

---

# 12. WEEK 10 — SANDBOXED PYTHON VÀ APPROVED FILE OPERATIONS

## 12.1 Mục tiêu tuần

Cho phép phân tích Python tùy biến khi tool registry không đủ, nhưng giữ Safe Tool Mode là mặc định và xây ranh giới thực thi có thể kiểm tra.

> **Lưu ý kỹ thuật quan trọng:** một Python subprocess thông thường không phải security sandbox (môi trường cách ly bảo mật) đáng tin cậy. Nếu chưa có container/VM isolation phù hợp, giữ capability này ở trạng thái disabled và chỉ hoàn thành interface + policy + tests bằng fake backend. Không quảng cáo subprocess đơn thuần là sandbox an toàn.

## 12.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W10-T01 | P0 | Threat model và chọn sandbox backend | 1,5h | Security decision record |
| W10-T02 | P0 | Thiết kế sandbox interface | 1h | Backend-independent contract |
| W10-T03 | P0 | Implement policy scanner | 2h | Allow/deny decision |
| W10-T04 | P0 | Implement isolated execution backend | 2,5h | Bounded container backend hoặc disabled safe fallback |
| W10-T05 | P0 | Resource/output limits | 1h | CPU/time/memory/file limits |
| W10-T06 | P0 | Generated-code review flow | 1,5h | Plan → scan → execute → verify |
| W10-T07 | P0 | Filesystem permission layer | 1,5h | Project-scoped create/edit |
| W10-T08 | P0 | Approved file operations | 1h | Create/edit/save; delete disabled |
| W10-T09 | P0 | Adversarial safety tests | 2h | Escape attempts blocked |

Tổng dự kiến: **14 giờ**.

## 12.3 Chi tiết task

### [ ] W10-T01 — Threat model và backend decision

Liệt kê assets cần bảo vệ:

- credentials;
- host filesystem;
- source repository;
- raw data;
- network;
- CPU/RAM/disk;
- running services.

Threats:

- đọc file ngoài project;
- ghi đè source/raw data;
- gọi network;
- chạy shell/subprocess;
- import package nguy hiểm;
- infinite loop/memory bomb;
- symlink escape;
- output quá lớn;
- package installation.

Chọn một trong hai kết quả hợp lệ:

1. Container/VM backend có isolation và giới hạn thực tế.
2. Capability disabled, nhưng interface/policy/test harness hoàn chỉnh để bổ sung sau.

### [ ] W10-T02 — Sandbox interface

Contract:

```text
ExecutionRequest
├── code
├── approved_inputs
├── allowed_libraries
├── temp_output_dir
├── limits
└── mutation_intent

ExecutionResult
├── status
├── stdout_summary
├── stderr_summary
├── artifacts
├── resource_usage
├── policy_findings
└── verification
```

### [ ] W10-T03 — Policy scanner

Scanner kiểm tra AST/import/calls và execution manifest. Nó là một lớp bảo vệ, không phải lớp duy nhất.

Block:

```text
os/system/subprocess
socket/network clients
package installation
dynamic import ngoài allowlist
credential/environment access
path traversal
unapproved file write
```

### [ ] W10-T04 — Isolated backend

Nếu dùng container:

- network disabled;
- read-only root filesystem;
- chỉ mount approved input read-only;
- chỉ mount temp output writable;
- non-root user;
- resource/time limit;
- no Docker socket;
- remove container sau run.

Nếu local Windows chưa chạy được container an toàn, implement `SandboxUnavailable` và giữ advanced mode off; Safe Tool Mode vẫn hoạt động đầy đủ.

### [ ] W10-T05 — Limits

Cấu hình:

```text
wall_time_seconds
cpu_limit
memory_mb
input_size_mb
output_size_mb
max_files
max_stdout_chars
max_retries
```

Khi vượt giới hạn, terminate run và trả lý do có cấu trúc.

### [ ] W10-T06 — Generated-code review flow

Flow:

```text
trusted tools insufficient
→ create analysis plan
→ generate code
→ policy scan
→ show planned mutation if any
→ obtain approval if required
→ isolated execution
→ capture outputs
→ verify artifact/result
→ evidence-based response
```

Không retry bằng cách nới quyền tự động.

### [ ] W10-T07 — Filesystem permission layer

Operations:

```text
read within approved project root
create with approval
edit with approval
overwrite with explicit approval
delete disabled
```

Kiểm tra canonical path và symlink trước khi truy cập.

### [ ] W10-T08 — Approved file operations

Cho phép:

- tạo report;
- tạo notebook helper;
- tạo config;
- sửa docs;
- lưu plot;
- lưu cleaned dataset.

Mọi write cần proposed path, overwrite state, reversibility và approval scope.

### [ ] W10-T09 — Adversarial tests

Test ít nhất:

- `../` path traversal;
- symlink ra ngoài root;
- đọc environment variable;
- network request;
- subprocess/shell;
- package install;
- infinite loop;
- allocate memory lớn;
- ghi raw data;
- ghi đè artifact không approval;
- tạo quá nhiều file;
- huge stdout.

Tất cả disallowed operations phải fail closed (khi không chắc chắn thì chặn).

## 12.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 |
| 3 | T04 |
| 4 | T05 + T06 |
| 5 | T07 + T08 |
| 6 | T09 + security review |

## 12.5 Gate cuối tuần

- [ ] Safe Tool Mode vẫn là mặc định.
- [ ] Host subprocess không bị gọi là security sandbox nếu thiếu isolation.
- [ ] Network/shell/credential/package install bị chặn.
- [ ] File access chỉ trong approved root.
- [ ] Delete vẫn disabled.
- [ ] Tất cả adversarial tests pass theo hướng bị chặn.

---

# 13. WEEK 11 — FREIGHT/LOGISTICS SHOWCASE, MCP VÀ MULTI-AGENT EXPERIMENT

## 13.1 Mục tiêu tuần

Chứng minh utility trên freight/logistics bằng một workflow end-to-end, đồng thời thực hiện hai experiment nhỏ để học công nghệ mới mà không phá vỡ core architecture.

## 13.2 Quy tắc time-box

- Freight showcase: 9–10 giờ, là P0.
- MCP experiment: tối đa 2 giờ, P1 nhưng cần ghi kết luận.
- Multi-agent experiment: tối đa 2 giờ, P1 nhưng cần ghi kết luận.
- Nếu core Week 1–10 chưa ổn, hoãn implementation experiment; vẫn viết experiment design và benchmark plan.

## 13.3 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W11-T01 | P0 | Chốt freight business definitions | 1h | Glossary + KPI rules |
| W11-T02 | P0 | Chuẩn bị demo dataset + data dictionary | 1,5h | Reproducible domain dataset |
| W11-T03 | P0 | Viết freight skill và references | 2h | Domain skill hoàn chỉnh |
| W11-T04 | P0 | Implement freight KPI/analysis adapters | 1,5h | KPI computation/query pack |
| W11-T05 | P0 | Xây delay/leakage/modeling workflow | 2h | Domain E2E workflow |
| W11-T06 | P0 | Chạy demo end-to-end + fix | 1,5h | Demo artifacts |
| W11-T07 | P1 | MCP experiment | 2h | Keep/drop decision |
| W11-T08 | P1 | Multi-agent experiment | 2h | Comparative benchmark |
| W11-T09 | P0 | Domain evaluation và documentation | 1h | Milestone E report |

Tổng dự kiến: **10,5 giờ P0; tối đa 14,5 giờ nếu làm cả hai experiment**. Nếu core cần sửa thêm, giảm mỗi experiment còn 1–1,5 giờ và ưu tiên freight showcase.

## 13.4 Chi tiết task

### [ ] W11-T01 — Business definitions

Định nghĩa:

```text
shipment
carrier
lane
route
origin
destination
freight_cost
transit_time
ETA
actual_delivery
on_time_delivery
delay
distance
```

KPI rules cần chốt:

- On-Time Delivery Rate dùng điều kiện nào?
- Delay tính theo giờ hay ngày?
- Shipment bị hủy có nằm trong denominator không?
- Missing actual delivery xử lý ra sao?
- Cost per distance xử lý distance bằng 0 thế nào?
- Route và lane có cùng nghĩa trong demo không?

### [ ] W11-T02 — Demo dataset

Yêu cầu:

- có data dictionary;
- có target candidate `is_delayed` hoặc target được tính theo rule đã chốt;
- có numeric, categorical, date/time, missing và outlier;
- có ít nhất một leakage candidate như `actual_delivery_time` khi dự đoán trước giao hàng;
- kích thước đủ chạy local nhanh;
- license/source được ghi rõ nếu dùng dữ liệu public.

Tạo một sample nhỏ cho automated tests và một bản lớn hơn cho demo.

### [ ] W11-T03 — Freight skill

Cấu trúc:

```text
.agents/skills/freight-logistics/
├── SKILL.md
└── references/
    ├── glossary.md
    ├── kpis.md
    ├── delay_analysis.md
    ├── feature_ideas.md
    └── leakage_rules.md
```

Skill phải tái sử dụng core tools/workflows; không copy lại toàn bộ code riêng cho logistics.

### [ ] W11-T04 — KPI/analysis adapters

Tạo các phép phân tích:

```text
On-Time Delivery Rate
Average Delay
Transit Time
Cost per Shipment
Cost per Distance
Carrier Performance
Route Performance
```

Ưu tiên SQL query pack hoặc cấu hình KPI; chỉ viết domain-specific Python tool khi core tool không thể biểu diễn hợp lý.

### [ ] W11-T05 — Domain workflow

Flow:

```text
Shipment dataset
→ profiling
→ data quality
→ business/target discussion
→ human confirmation
→ EDA
→ SQL business analysis
→ delay analysis
→ leakage review
→ human approval
→ preprocessing
→ baseline prediction
→ evaluation
→ business summary
```

Tạo checkpoint để demo không phải chạy lại toàn bộ nếu một step cuối lỗi.

### [ ] W11-T06 — End-to-end demo

Demo phải thể hiện rõ ba điều:

1. Copilot làm nhanh công việc tay chân.
2. Copilot đưa evidence và recommendation.
3. Data Scientist vẫn quyết định target, prediction moment, leakage, metric, split và model.

Artifacts:

- Data Quality Report;
- 3–5 charts;
- SQL results;
- approval record;
- experiment comparison;
- business summary.

### [ ] W11-T07 — MCP experiment

Chọn đúng một use case:

```text
project metadata resource
hoặc experiment-results resource
hoặc read-only dataset catalog
```

So sánh trước/sau theo:

```text
reuse
interoperability
tool exposure
architecture clarity
implementation cost
```

Kết luận bắt buộc: `KEEP`, `DEFER` hoặc `DROP`, kèm evidence. Không chuyển mọi core tool sang MCP.

### [ ] W11-T08 — Multi-agent experiment

Experimental branch/logical configuration:

```text
Root Copilot
├── SQL Specialist
└── ML Specialist
```

Dùng cùng 10 task để so với single Copilot:

- 4 SQL tasks;
- 4 ML workflow tasks;
- 2 mixed tasks.

Đo:

```text
task_success
latency
LLM_calls
tool_calls
failure_rate
maintainability_note
```

Chỉ `KEEP` nếu lợi ích đủ lớn và không làm safety/routing phức tạp không cần thiết.

### [ ] W11-T09 — Domain evaluation

Tối thiểu 10 freight tasks:

- KPI definitions;
- carrier/route SQL analysis;
- leakage detection;
- target/prediction-time clarification;
- approved preprocessing;
- baseline evaluation;
- unsafe request.

## 13.5 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 |
| 3 | T04 + T05 phần 1 |
| 4 | Hoàn thành T05 + T06 |
| 5 | T07 time-boxed |
| 6 | T08 time-boxed + T09 |

## 13.6 Gate cuối tuần

- [ ] Freight skill dùng lại core architecture.
- [ ] Domain definitions và KPI denominator rõ ràng.
- [ ] Leakage theo prediction moment được phát hiện và hỏi human.
- [ ] Demo end-to-end tạo đủ artifacts.
- [ ] MCP có kết luận keep/defer/drop.
- [ ] Multi-agent có benchmark so với single Copilot, không giữ chỉ để trình diễn.

---

# 14. WEEK 12 — FULL EVALUATION, STREAMLIT VÀ PORTFOLIO

## 14.1 Mục tiêu tuần

Đóng gói Copilot thành một sản phẩm có số liệu đánh giá, giao diện demo và câu chuyện portfolio rõ ràng. Tuần này ưu tiên integration, reliability và evidence; không thêm capability lớn mới.

## 14.2 Danh sách task

| ID | Priority | Task | Thời lượng | Output chính |
|---|---:|---|---:|---|
| W12-T01 | P0 | Hợp nhất evaluation dataset 100–150 tasks | 1,5h | Full benchmark set |
| W12-T02 | P0 | Xây evaluation runner + graders | 1,5h | Reproducible eval command |
| W12-T03 | P0 | Chạy benchmark và triage failures | 2h | Metrics + failure taxonomy |
| W12-T04 | P0 | Bổ sung observability | 1,5h | Structured run log |
| W12-T05 | P0 | Xây Streamlit UI | 2,5h | Demo interface |
| W12-T06 | P0 | Chuẩn bị ba demo scenarios | 1,5h | Repeatable demo scripts |
| W12-T07 | P0 | Hoàn thiện README + docs + diagrams | 1,5h | Portfolio documentation |
| W12-T08 | P0 | Screenshots và demo video | 1h | Portfolio media |
| W12-T09 | P0 | Release checklist + final safety run | 1h | V1 release candidate |
| W12-T10 | P2 | Persistent state đơn giản | 1,5h | JSON/SQLite state nếu core ổn |

Tổng dự kiến: **14 giờ P0; persistent state chỉ làm nếu toàn bộ P0 đã đạt**.

## 14.3 Chi tiết task

### [ ] W12-T01 — Hợp nhất evaluation set

Target: 100–150 tasks. Phân bổ tham khảo:

| Category | Số task mục tiêu |
|---|---:|
| Tool calls | 20 |
| Skill selection | 15 |
| Routing/workflow | 15 |
| Data quality | 20 |
| EDA/statistics | 15 |
| SQL | 20 |
| Preprocessing/HITL | 20 |
| ML | 20 |
| Freight | 10 |
| Safety/adversarial | 10 |

Một task có thể mang nhiều label nên tổng category có thể lớn hơn số task unique.

Mỗi task cần:

```text
task_id
category
prompt
fixtures
initial_state
expected_behavior
expected_tools_or_workflow
required_evidence
safety_expectation
grader
```

### [ ] W12-T02 — Evaluation runner và graders

Runner phải:

- chạy một task hoặc toàn bộ suite;
- cố định model/config/version;
- lưu raw structured outputs;
- không thay đổi expected result;
- resume được task chưa chạy nếu bị ngắt;
- xuất summary dạng Markdown/JSON.

Graders ưu tiên deterministic checks trước LLM judge:

- exact/schema/result checks;
- numeric tolerance;
- expected tool/workflow;
- prohibited action checks;
- evidence reference checks.

### [ ] W12-T03 — Benchmark và triage

Đo:

```text
tool_selection_accuracy
tool_argument_accuracy
structured_output_validity
skill_selection_accuracy
workflow_completion_rate
SQL_execution_accuracy
unsafe_SQL_execution_rate
approval_compliance
mutation_without_approval
unsupported_claim_rate
task_success_rate
average_LLM_calls
average_tool_calls
latency
```

Failure taxonomy:

```text
model
prompt/skill
router
schema
tool
workflow
state
approval
data fixture
grader
environment
```

Chỉ sửa lỗi P0/critical trong tuần này. Lỗi nice-to-have đưa vào post-V1 backlog.

### [ ] W12-T04 — Observability

Mỗi run lưu:

```text
run_id
user_request
selected_skill
selected_workflow
reasoning_decision_summary
tools_called
arguments
tool_outputs_summary
recommendations
approval_requests
human_decisions
state_before
state_after
artifacts
errors
latency
```

Không lưu hidden chain-of-thought. Chỉ lưu decision/routing summary ngắn. Redact secrets và hạn chế row-level data trong log.

### [ ] W12-T05 — Streamlit UI

Màn hình tối thiểu:

```text
Chat
Project/session panel
Active dataset
Evidence/charts
Approval request
Decision log
Experiment summary
```

Response cards:

```text
Finding
Evidence
Recommendation
Human Decision Required
```

UI không bypass permission layer. Nút Approve phải gửi approval decision vào cùng backend policy đã dùng trong CLI.

### [ ] W12-T06 — Ba demo scenarios

#### Demo 1 — Dataset Health Check

Prompt:

```text
Analyze this shipment dataset before modeling.
```

Thể hiện profiling, missing, duplicate, ID, outlier, balance và leakage; không mutation.

#### Demo 2 — SQL + EDA business analysis

Prompt:

```text
Which carriers and routes have the worst delivery performance?
```

Thể hiện schema grounding, safe SQL, KPI, chart và evidence-based summary.

#### Demo 3 — Human-controlled delay baseline

Prompt:

```text
I want to predict whether a shipment will arrive late.
```

Copilot phải dừng để xác nhận target, prediction moment, leakage, metric, split và features trước khi train.

Mỗi demo có:

- input dataset version;
- exact prompt sequence;
- expected checkpoints;
- expected artifacts;
- fallback nếu local model output lệch;
- thời lượng mục tiêu 2–4 phút.

### [ ] W12-T07 — Portfolio documentation

Hoàn thiện:

```text
README.md
docs/architecture.md
docs/human_ai_boundary.md
docs/safety_model.md
docs/decisions.md
evaluation_report.md
three_demo_scenarios.md
```

README nên có:

1. Problem statement.
2. Copilot làm gì và không làm gì.
3. Architecture.
4. Quick start.
5. Supported workflows.
6. Human approval example.
7. Evaluation results.
8. Freight demo.
9. Limitations.
10. Roadmap.

Portfolio story:

> I built a local-first Personal Data Science Copilot that automates repetitive analytical workflows while keeping critical data and modeling decisions under human control.

Không dùng claim “AI Data Scientist tự động làm mọi thứ”.

### [ ] W12-T08 — Screenshots và video

Screenshots tối thiểu:

- profiling/data-quality report;
- approval card;
- SQL + chart;
- experiment comparison;
- Streamlit overview.

Video 3–5 phút:

1. Bài toán.
2. Kiến trúc ngắn.
3. Demo strongest scenario.
4. Safety/HITL.
5. Evaluation numbers.

### [ ] W12-T09 — Final release checklist

Chạy:

- fresh install test;
- full unit/integration/safety suite;
- full eval hoặc fixed representative suite;
- three demos;
- broken-path checks;
- README link checks;
- secret scan;
- repository size check.

Tag version `v1.0.0` chỉ khi critical gates đạt.

### [ ] W12-T10 — Optional persistent state

Chỉ làm nếu core ổn định. Có thể dùng `project_state.json` hoặc SQLite để lưu:

```text
dataset references
confirmed target
approved decisions
completed workflows
experiments
artifact references
```

Đây là project state, không phải long-term conversational memory.

## 14.4 Lịch làm theo ngày

| Ngày | Task |
|---|---|
| 1 | T01 + T02 |
| 2 | T03 + triage critical failures |
| 3 | T04 + T05 phần 1 |
| 4 | Hoàn thành T05 + T06 |
| 5 | T07 + T08 |
| 6 | T09; T10 chỉ khi còn thời gian và core đã pass |

## 14.5 Gate cuối tuần

- [ ] Benchmark có 100–150 tasks và reproducible runner.
- [ ] `mutation_without_approval = 0`.
- [ ] `unsafe_SQL_execution_rate = 0`.
- [ ] Streamlit dùng cùng backend policy với CLI.
- [ ] Ba demo chạy lặp lại được.
- [ ] Có evaluation report, limitations và roadmap.
- [ ] Repo cài được từ môi trường sạch.

---

# 15. WEEKLY REVIEW TEMPLATE

Sao chép block này vào `docs/dev_journal.md` cuối mỗi tuần:

```markdown
## Week XX Review

### Mục tiêu tuần
- ...

### Task hoàn thành
- [x] WXX-T...

### Task chưa hoàn thành
- [ ] WXX-T... — Lý do: ...

### Demo chạy được
- Input:
- Prompt/command:
- Output:

### Metrics
- metric_1:
- metric_2:

### Bugs/failure cases quan trọng
1. ...

### Quyết định kiến trúc
1. Quyết định:
   - Evidence:
   - Trade-off:

### Điều đã học và có thể tự giải thích
1. ...

### Technical debt
1. ...

### Kế hoạch tuần sau
1. ...
```

---

# 16. TASK BOARD TEMPLATE

| ID | Task | Priority | Estimate | Actual | Status | Blocker | Evidence/PR/Commit |
|---|---|---:|---:|---:|---|---|---|
| WXX-T01 |  | P0 |  |  | TODO |  |  |
| WXX-T02 |  | P0 |  |  | TODO |  |  |
| WXX-T03 |  | P1 |  |  | TODO |  |  |

Quy tắc dùng board:

- Chỉ có tối đa hai task `IN PROGRESS` cùng lúc.
- Ghi `Actual` sau khi hoàn thành để điều chỉnh estimate các tuần sau.
- Mỗi blocker quá 60 phút phải ghi lại và chọn: tự giải quyết, giảm scope hoặc đưa vào backlog.
- Link evidence có thể là commit, test output, eval report, screenshot hoặc artifact.

---

# 17. BACKLOG VÀ QUY TẮC CẮT GIẢM

## 17.1 Không được cắt

```text
structured tool contracts
raw-data immutability
approval enforcement
SQL write blocking
sandbox/file safety tests
dummy baseline comparison
continuous evaluation
limitations documentation
```

## 17.2 Cắt đầu tiên khi thiếu thời gian

```text
UI polish
thêm model thứ ba
thêm chart ít quan trọng
MCP implementation sâu
multi-agent optimization
persistent state
SHAP
PostgreSQL
MLflow
cloud providers
```

## 17.3 Điều kiện chuyển task sang Post-V1

Chuyển nếu thỏa một trong các điều kiện:

- không cần để ba demo chính hoạt động;
- không ảnh hưởng critical safety metrics;
- cần thêm hạ tầng/phần cứng ngoài phạm vi local V1;
- không có evaluation chứng minh utility;
- chỉ làm dự án “trông giống agent hiện đại” nhưng không giảm công việc lặp lại.

---

# 18. DEPENDENCY MAP

```text
W1 Reliable Tools
 ↓
W2 Local LLM + Tool Calling
 ↓
W3 Skills
 ↓
W4 Orchestrator + Workflows + CLI
 ↓
W5 Quality + Approval
 ↓
W6 EDA/Statistics ─────┐
 ↓                    │
W7 Safe SQL           │
 ↓                    │
W8 Preprocessing/FE ←─┘
 ↓
W9 Baseline ML
 ↓
W10 Sandbox/File Safety
 ↓
W11 Freight Showcase + Experiments
 ↓
W12 Evaluation + Streamlit + Portfolio
```

Không nên bắt đầu:

- Week 8 trước khi approval system của Week 5 chạy đúng;
- Week 9 trước khi leakage review và preprocessing pipeline ổn định;
- Week 10 trước khi filesystem permission model được xác định;
- Week 11 domain demo trước khi core workflows chạy end-to-end;
- Week 12 UI polish trước khi benchmark và safety gates có kết quả.

---

# 19. FINAL DEFINITION OF DONE CHO V1

## Runtime và architecture

- [ ] Chạy local-first và không bắt buộc paid OpenAI API.
- [ ] `LLMProvider` có thể thay thế.
- [ ] Core DS logic nằm trong tools/workflows, không chỉ ở prompt.
- [ ] Một orchestrator là kiến trúc mặc định.
- [ ] Skills có version, trigger và validation.

## Data và tools

- [ ] Hỗ trợ CSV, Excel, Parquet và DuckDB.
- [ ] Có ít nhất 20 tools đáng tin cậy.
- [ ] Raw data immutable.
- [ ] Structured input/output được validate.
- [ ] Tool chạy độc lập với LLM.

## Human control

- [ ] Target và prediction moment do human xác nhận.
- [ ] Leakage quan trọng do human xác nhận.
- [ ] Split, metric, feature set và model list do human approve.
- [ ] Mutation luôn qua approval gate.
- [ ] Decision log tái tạo được preprocessing decision.

## Security

- [ ] SQL writes bị chặn.
- [ ] Arbitrary host Python bị chặn.
- [ ] Advanced Python chỉ chạy trong isolation phù hợp hoặc capability bị disabled.
- [ ] File operations bị giới hạn trong approved root.
- [ ] Delete disabled trong V1.
- [ ] Mutation without approval bằng 0.

## ML

- [ ] Có classification và regression baseline workflow.
- [ ] Có Dummy baseline.
- [ ] Preprocessing chỉ fit trên train.
- [ ] Experiment metadata được lưu.
- [ ] Có error analysis cơ bản.

## Evaluation và portfolio

- [ ] Unit, integration, safety và agent evals chạy được.
- [ ] Full benchmark 100–150 tasks.
- [ ] Evaluation report công khai cả limitations.
- [ ] CLI và Streamlit dùng cùng core backend.
- [ ] Ba portfolio demos chạy lặp lại được.
- [ ] Có README, architecture, safety model, human–AI boundary, screenshots và demo video.

---

# 20. KẾT LUẬN THỰC THI

Trong 12 tuần, mục tiêu không phải là xây một “AI Data Scientist tự động quyết định mọi thứ”. Mục tiêu là tạo một Copilot thật sự hữu ích:

```text
Reliable execution
+
Clear evidence
+
Reproducible workflows
+
Human approval for consequential decisions
+
Measured performance and safety
```

Nếu phải lựa chọn giữa thêm một capability mới và làm capability hiện có đáng tin cậy hơn, ưu tiên độ tin cậy. Đây cũng là điểm mạnh nhất của dự án khi trình bày trong portfolio hoặc phỏng vấn Data Scientist.
