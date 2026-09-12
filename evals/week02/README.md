# Week 02 Golden Prompts

## Mục tiêu

`golden_prompts.json` là bộ ground truth dùng để đánh giá khả năng routing của
Local LLM. Mỗi case mô tả một yêu cầu của người dùng, tool được kỳ vọng sẽ được
chọn và arguments tương ứng.

## Phạm vi

Bộ prompt bao phủ 7 tool của Week 1:

- `check_missing`
- `check_duplicates`
- `check_cardinality`
- `check_constant_columns`
- `detect_id_candidates`
- `describe_numeric`
- `describe_categorical`

Mỗi prompt chỉ có đúng một `expected_tool` vì capability hiện tại hỗ trợ một
request → một tool → một lần execute → final answer. Bộ này chưa đánh giá
multi-tool planning.

## Schema của một golden case

Mỗi phần tử trong `golden_prompts.json` có đúng các field sau:

```json
{
  "id": "unique_case_id",
  "category": "direct",
  "prompt": "User request",
  "expected_tool": "tool_name",
  "expected_arguments": {}
}
```

- `id`: định danh duy nhất, viết thường và ổn định giữa các lần chạy.
- `category`: nhóm của prompt.
- `prompt`: yêu cầu tự nhiên của người dùng.
- `expected_tool`: tool đúng theo capability hiện tại.
- `expected_arguments`: JSON object truyền vào tool. Chỉ `describe_categorical`
  có thể có `top_k`; nếu prompt không nêu số lượng thì object này là `{}`.

## Nhóm test

- `direct`: yêu cầu rõ ràng, trực tiếp về một tool.
- `paraphrase`: cùng ý định với tool nhưng dùng wording khác.
- `argument_sensitive`: kiểm tra việc trích xuất chính xác `top_k` cho
  `describe_categorical`, bao gồm cả trường hợp dùng giá trị mặc định.
- `ambiguous_resolvable`: cách diễn đạt tự nhiên hơn nhưng vẫn có một tool hợp
  lý nhất trong capability hiện tại.

## Nguyên tắc ground truth

- `expected_tool` và `expected_arguments` được xác định từ capability hiện tại
  của tool, không dựa trên kết quả thực tế của model.
- Không thay đổi ground truth chỉ để model đạt điểm cao hơn.
- Nếu một prompt thực sự ambiguous, cần sửa prompt để ý định rõ hơn thay vì
  tùy ý chọn một đáp án.

## Metrics dùng ở W02-T08

Các metrics dưới đây chỉ được mô tả ở đây; chưa có số liệu nào được tính trong
W02-T07:

- JSON validity: output routing có phải JSON hợp lệ hay không.
- Tool selection accuracy: model chọn đúng `expected_tool` đến mức nào.
- Argument accuracy: arguments model tạo ra có khớp `expected_arguments` hay
  không.
- Latency: thời gian xử lý request.

## Giới hạn

Bộ golden prompts hiện tại:

- chưa test multi-tool;
- chưa test planner;
- chưa test LangGraph;
- chưa test malformed output recovery;
- chưa test dataset-specific factual correctness.
