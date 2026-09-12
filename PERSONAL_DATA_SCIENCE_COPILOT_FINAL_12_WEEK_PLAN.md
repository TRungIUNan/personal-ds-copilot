# PERSONAL DATA SCIENCE COPILOT
## Final 12-Week Build Plan — Local-First, Human-in-the-Loop, Utility-First, Production-Oriented

> **Primary goal:** build a Personal Data Science Copilot that reduces repetitive, mechanical Data Science work while keeping important analytical and modeling decisions under human control.

> **Priority order:** Utility → Architecture Quality → New Technology.

> **Core principle:** Reliable tools before agents. Deterministic workflows before autonomous reasoning. Evidence before recommendations. Human approval before consequential actions.

---

# 0. PRODUCT DECISIONS — CHỐT THEO LỰA CHỌN CÁ NHÂN

## 0.1 Công việc ưu tiên

Copilot V1 ưu tiên 8 nhóm công việc:

1. Data loading / profiling.
2. Data quality.
3. EDA + visualization.
4. Statistical analysis.
5. SQL / database querying.
6. Data cleaning / preprocessing.
7. Feature engineering.
8. Baseline machine learning.

Không ưu tiên trong core V1:

- AutoML;
- final model selection hoàn toàn tự động;
- autonomous deployment;
- deep learning;
- Spark/distributed processing;
- complex RAG;
- long-term personal memory;
- nhiều agent chỉ để trình diễn.

---

## 0.2 Nguồn dữ liệu

Copilot phải hỗ trợ cả:

```text
FILES
├── CSV
├── Excel
└── Parquet

DATABASE
└── DuckDB first
    └── PostgreSQL adapter later
```

Mục tiêu là cùng một Copilot có thể xử lý:

```text
"Analyze this CSV."
```

và:

```text
"Which routes have the highest average delay?"
```

trên database.

---

## 0.3 Python execution

Thiết kế hai chế độ:

### DEFAULT — SAFE TOOL MODE

```text
LLM
 ↓
Approved tool registry
 ↓
Trusted Python implementation
 ↓
Structured result
```

Đây là chế độ mặc định.

### ADVANCED — SANDBOXED PYTHON MODE

```text
User request
 ↓
Copilot decides advanced analysis is needed
 ↓
Generate code
 ↓
Sandbox policy check
 ↓
Isolated execution
 ↓
Capture output
 ↓
Explain evidence
```

Sandbox chỉ được thêm sau khi Safe Tool Mode ổn định.

Không cho generated Python chạy trực tiếp trong host process.

---

## 0.4 Data cleaning autonomy

Mặc định:

```text
DETECT
  ↓
SHOW EVIDENCE
  ↓
RECOMMEND
  ↓
HUMAN APPROVE
  ↓
EXECUTE
  ↓
VERIFY
  ↓
LOG DECISION
```

Copilot không tự:

- drop column;
- drop rows;
- impute;
- encode;
- transform;
- overwrite cleaned dataset

nếu chưa được approve.

---

## 0.5 ML autonomy

ML workflow:

```text
Copilot recommends
        ↓
Human approves
        ↓
Copilot trains
        ↓
Copilot evaluates
        ↓
Copilot compares
        ↓
Copilot reports
        ↓
Human chooses
```

Không build AutoML trong V1.

---

## 0.6 Project files

Copilot được phép:

```text
READ
→ automatic if within approved project root

CREATE
→ approval required

EDIT
→ approval required

OVERWRITE
→ explicit approval required

DELETE
→ disabled in V1
```

---

## 0.7 Interface

Development order:

```text
CLI
 ↓
Streamlit UI
```

CLI là interface kỹ thuật đầu tiên.

Streamlit là interface demo/portfolio.

---

## 0.8 Domain

Core architecture:

```text
GENERAL DATA SCIENCE COPILOT
```

Portfolio domain:

```text
FREIGHT / LOGISTICS
```

Freight/Logistics được implement dưới dạng domain skill + demo dataset, không hard-code vào core.

---

## 0.9 Project memory

Trong core V1:

```text
Session State
+
Project State in current run
```

Persistent cross-session memory:

```text
LATE V1 / V1.1
```

Không để persistent memory làm chậm core product.

---

# 1. PRODUCT VISION

Data Scientist không cần thêm một chatbot biết giải thích machine learning.

Data Scientist cần một hệ thống có thể giảm những công việc như:

```text
open file
inspect shape
inspect dtypes
check missing
check duplicates
check cardinality
generate statistics
generate standard plots
inspect target
find suspicious columns
write repetitive SQL
calculate KPIs
run approved preprocessing
train baseline
calculate metrics
compare experiments
save plots
create analysis summary
update report
```

Copilot nên tự động hóa execution.

Data Scientist tập trung vào:

```text
business problem
target definition
prediction moment
assumption validation
leakage confirmation
metric choice
FP/FN trade-off
experimental design
feature meaning
business interpretation
final model decision
production decision
```

---

# 2. PRODUCT BOUNDARY

## AI MAY AUTOMATE

```text
Load data
Inspect schema
Calculate missing rates
Detect duplicates
Calculate cardinality
Detect obvious constants
Generate descriptive statistics
Generate standard plots
Calculate correlations
Run approved statistical tests
Execute read-only SQL
Generate candidate preprocessing plan
Execute approved preprocessing
Generate feature candidates
Execute approved feature transforms
Train approved baseline models
Calculate metrics
Compare experiments
Save plots
Generate reports
Generate experiment metadata
```

---

## AI MAY RECOMMEND

```text
Possible target
Possible ID
Possible leakage
Possible outlier treatment
Missing-value strategy
Encoding strategy
Scaling strategy
Feature transformation
Feature candidate
Metric candidate
Split strategy
Candidate models
Threshold
Next experiment
Business interpretation
```

---

## HUMAN MUST DECIDE

```text
Business objective
Final target
Prediction moment
Definition of success
Leakage confirmation
Whether to remove data
Final imputation strategy
Feature inclusion/exclusion
Validation strategy
Main evaluation metric
FP/FN cost
Final model selection
Production decision
```

---

# 3. FINAL ARCHITECTURE

```text
                         DATA SCIENTIST
                               │
                               ▼
                    ┌─────────────────────┐
                    │     DS COPILOT      │
                    │ LANGGRAPH RUNTIME   │
                    └──────────┬──────────┘
                               │
                      INTENT + CONTEXT
                               │
                    TYPED GRAPH / PROJECT STATE
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
       SKILLS              WORKFLOWS              TOOLS
          │                    │                    │
   procedures/knowledge   deterministic flow    execution
          │                    │                    │
          └──────────────┬─────┴──────────────┬────┘
                         │                    │
                         ▼                    ▼
                    STRUCTURED           SANDBOX
                     RESULTS          ADVANCED PYTHON
                         │                    │
                         └──────────┬─────────┘
                                    ▼
                             EVIDENCE LAYER
                                    │
                                    ▼
                            RECOMMENDATION
                                    │
                                    ▼
                      INTERRUPT / APPROVAL GATE
                                    │
                              approved?
                              /       \
                            no         yes
                            │           │
                            ▼           ▼
                          stop       execute
                                        │
                                        ▼
                                     verify
                                        │
                                        ▼
                                  DECISION LOG
                                        │
                                        ▼
                              RESULTS / REPORTS
```

LangGraph is used only as the orchestration runtime:

```text
StateGraph          → top-level Copilot orchestration
CopilotState        → typed state shared across nodes
Nodes               → routing, reasoning and execution steps
Conditional edges   → deterministic route decisions
Subgraphs           → reusable DS workflows
Checkpointer        → session continuity and resumable execution
interrupt()         → pause before consequential action
Command(resume=...) → continue after human decision
```

Tools, Skills, approval policy, Data Science logic and LLM providers remain independently testable outside LangGraph.

---

# 4. FIVE CORE LAYERS

## Layer 1 — Tools

Tools are deterministic execution primitives.

Examples:

```text
load_csv()
get_schema()
check_missing()
check_duplicates()
detect_outliers()
calculate_correlation()
run_chi_square()
execute_readonly_sql()
apply_imputation()
encode_categorical()
train_baseline()
evaluate_model()
save_plot()
```

A tool should not decide business meaning.

---

## Layer 2 — Skills

A skill encodes:

```text
how to perform a class of work
when to use a workflow
what evidence is needed
what risks to check
what not to conclude
when human approval is required
```

Target skills:

```text
01 data-profiling
02 data-quality
03 leakage-analysis
04 eda
05 statistical-analysis
06 sql-analysis
07 preprocessing
08 feature-engineering
09 baseline-modeling
10 model-evaluation
11 freight-logistics
```

Quality > quantity.

---

## Layer 3 — Workflows

Known process = deterministic workflow.

Each major workflow is implemented as a LangGraph subgraph or a deterministic node sequence. The graph controls order and branching; the LLM does not decide the order of fixed quality checks.

Example:

```text
DATA QUALITY

load
 ↓
schema
 ↓
missing
 ↓
duplicate
 ↓
cardinality
 ↓
constant columns
 ↓
IDs
 ↓
target review
 ↓
leakage candidates
 ↓
report
```

No reason to ask an LLM whether `missing` should come before or after `duplicate`.

---

## Layer 4 — Copilot Orchestrator with LangGraph

The Copilot:

```text
understands request
loads relevant state
selects skill
selects workflow
calls tools
observes results
requests clarification only when analytically necessary
shows evidence
recommends next action
requests approval
executes approved action
```

Implementation mapping:

```text
StateGraph
├── intake node
├── context node
├── skill-selection node
├── conditional router
├── workflow subgraphs
├── evidence/response node
├── approval interrupt node
└── verified action node
```

It is not allowed to silently make modeling-critical decisions.

---

## Layer 5 — Human

Human owns:

```text
meaning
judgment
assumptions
trade-offs
approval
final decisions
```

---

# 5. TECHNOLOGY STACK — 2026 TARGET

## Language

```text
Python 3.11+
```

---

## Data Science

```text
Pandas
NumPy
SciPy
scikit-learn
XGBoost
Matplotlib
Plotly
```

Optional later:

```text
Polars
SHAP
statsmodels
```

---

## File + SQL

```text
DuckDB
PyArrow
openpyxl
```

DuckDB provides a convenient local analytical SQL layer for file + database workflows.

PostgreSQL adapter can be added after V1.

---

## Schemas / Validation

```text
Pydantic
```

Use Pydantic for:

```text
tool inputs
tool results
approval requests
project state
experiment results
agent outputs
```

---

## Local LLM

```text
Ollama
```

Requirements for selected model:

```text
good instruction following
tool calling
structured output
sufficient context
acceptable latency on user's machine
```

Do not hard-code model name into business logic.

---

## LLM abstraction

```text
LLMProvider
├── OllamaProvider        # V1 required
├── GeminiProvider        # optional
├── OpenAIProvider        # optional
└── other adapters
```

---

## Orchestration framework

Primary:

```text
LangGraph
```

Reason:

```text
Explicit state graph
Deterministic + LLM-driven nodes
Conditional routing
Reusable workflow subgraphs
Checkpointed execution
Human-in-the-loop interrupts
Local model compatibility
Fine-grained control and testability
```

Recommended minimum integration:

```text
langgraph
langchain-core
langchain-ollama     # optional adapter inside OllamaProvider
```

Do not make the whole application depend on high-level LangChain agents.

LangGraph is the orchestration layer, not the location of Data Science business logic and not a security boundary.

Architecture must remain independent from LangGraph where practical:

```text
tools run without LangGraph
skills load without LangGraph
approval policy validates outside the graph
LLMProvider can be replaced
workflows expose typed input/output contracts
```

LangSmith is optional. Local pytest, custom evaluation datasets and structured local traces remain the V1 default.

---

## Agent Skills

Use open Agent Skills format:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

---

## MCP

MCP is included as an integration experiment near the end of V1.

It is NOT a prerequisite for core functionality.

Good first MCP integration:

```text
project resources / metadata
```

or:

```text
read-only analytical resource
```

Do not convert every local tool into MCP.

---

## Multi-agent

Not the core architecture.

Core:

```text
ONE COPILOT ORCHESTRATOR
+
TOOLS
+
SKILLS
+
WORKFLOWS
```

Later experiment:

```text
Orchestrator
├── SQL specialist
└── ML specialist
```

Only retain multi-agent if evaluation demonstrates an advantage.

---

# 6. EXECUTION MODES

## Mode 1 — Read-only

No approval required.

Examples:

```text
profile
statistics
visualization
read-only SQL
model metrics
file reading
```

---

## Mode 2 — Recommendation

Human review required.

Examples:

```text
possible leakage
outlier strategy
imputation proposal
feature candidate
metric recommendation
split recommendation
```

---

## Mode 3 — Mutating action

Explicit approval required.

Examples:

```text
drop column
drop rows
impute
encode
scale
create processed dataset
create/edit project file
train expensive model
overwrite artifact
```

---

## Mode 4 — Prohibited V1

```text
delete project files
run arbitrary shell commands
write SQL to production DB
deploy model automatically
install arbitrary packages automatically
access directories outside project root
execute generated Python outside sandbox
```

---

# 7. REPOSITORY STRUCTURE

```text
personal-ds-copilot/
│
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
│
├── config/
│   ├── settings.yaml
│   ├── models.yaml
│   ├── permissions.yaml
│   └── tools.yaml
│
├── .agents/
│   └── skills/
│       ├── data-profiling/
│       │   └── SKILL.md
│       ├── data-quality/
│       │   └── SKILL.md
│       ├── leakage-analysis/
│       │   └── SKILL.md
│       ├── eda/
│       │   └── SKILL.md
│       ├── statistical-analysis/
│       │   └── SKILL.md
│       ├── sql-analysis/
│       │   └── SKILL.md
│       ├── preprocessing/
│       │   └── SKILL.md
│       ├── feature-engineering/
│       │   └── SKILL.md
│       ├── baseline-modeling/
│       │   └── SKILL.md
│       ├── model-evaluation/
│       │   └── SKILL.md
│       └── freight-logistics/
│           ├── SKILL.md
│           └── references/
│
├── src/
│   ├── copilot/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   ├── router.py
│   │   ├── response_builder.py
│   │   └── prompts.py
│   │
│   ├── llm/
│   │   ├── base.py
│   │   ├── ollama_provider.py
│   │   └── schemas.py
│   │
│   ├── tools/
│   │   ├── registry.py
│   │   ├── data/
│   │   ├── quality/
│   │   ├── statistics/
│   │   ├── visualization/
│   │   ├── sql/
│   │   ├── preprocessing/
│   │   ├── features/
│   │   ├── ml/
│   │   └── filesystem/
│   │
│   ├── skills/
│   │   ├── registry.py
│   │   ├── loader.py
│   │   └── selector.py
│   │
│   ├── workflows/
│   │   ├── profiling.py
│   │   ├── data_quality.py
│   │   ├── eda.py
│   │   ├── statistical_analysis.py
│   │   ├── sql_analysis.py
│   │   ├── preprocessing.py
│   │   ├── baseline_ml.py
│   │   └── full_analysis.py
│   │
│   ├── state/
│   │   ├── checkpointer.py
│   │   ├── project_state.py
│   │   ├── experiment_state.py
│   │   └── decision_log.py
│   │
│   ├── approval/
│   │   ├── policy.py
│   │   ├── request.py
│   │   └── audit.py
│   │
│   ├── sandbox/
│   │   ├── interface.py
│   │   ├── policy.py
│   │   └── local_sandbox.py
│   │
│   ├── evaluation/
│   │   ├── tool_eval.py
│   │   ├── skill_eval.py
│   │   ├── routing_eval.py
│   │   ├── sql_eval.py
│   │   ├── hitl_eval.py
│   │   └── task_eval.py
│   │
│   └── utils/
│
├── cli/
│   └── main.py
│
├── app/
│   └── streamlit_app.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── safety/
│   ├── graph/
│   └── agent/
│
├── evals/
│   ├── datasets/
│   ├── golden_tasks/
│   ├── graders/
│   └── results/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── artifacts/
│   ├── plots/
│   ├── reports/
│   ├── models/
│   └── experiments/
│
└── docs/
    ├── architecture.md
    ├── human_ai_boundary.md
    ├── safety_model.md
    ├── decisions.md
    └── dev_journal.md
```

---

# 8. 12-WEEK ROADMAP

# WEEK 1 — RELIABLE DATA TOOLS

## Goal

Build deterministic, reusable tools before introducing an LLM.

## Learn

```text
function contracts
type hints
Pydantic
exception handling
pure functions
dependency injection basics
pytest
structured results
```

## Build — loaders

```text
load_csv()
load_excel()
load_parquet()
```

## Build — inspection

```text
get_shape()
get_schema()
get_dtypes()
get_column_summary()
preview_data()
```

## Build — quality

```text
check_missing()
check_duplicates()
check_cardinality()
check_constant_columns()
detect_id_candidates()
```

## Build — descriptions

```text
describe_numeric()
describe_categorical()
```

## Contract example

```text
MissingColumnResult
├── column
├── dtype
├── missing_count
├── missing_rate
├── severity
└── notes
```

## Unit tests

Test:

```text
normal dataset
empty dataframe
all-null column
duplicate rows
mixed dtype
constant column
high-cardinality string
file not found
unsupported format
```

## Deliverables

```text
src/tools/data/
src/tools/quality/
tests/unit/
```

## Evaluation from Week 1

Track:

```text
tool correctness
exception correctness
schema validation rate
```

## Pass criteria

```text
all core unit tests pass
no unstructured tool return
no tool modifies source data
```

---

# WEEK 2 — LOCAL LLM + STRUCTURED OUTPUT + TOOL CALLING

## Goal

Make local LLM reliably call Week-1 tools.

## Learn

```text
LLM context
system instruction
tool schema
function calling
structured output
JSON schema
Pydantic validation
tool result grounding
```

## Setup

```text
Ollama
+
one selected local model
```

Benchmark 2–3 models only if hardware permits.

Evaluate:

```text
tool selection
argument accuracy
latency
structured-output validity
```

## Build

```text
LLMProvider
OllamaProvider
ToolRegistry
ToolExecutor
```

`OllamaProvider` may wrap `ChatOllama`, but its public interface belongs to the project. Do not expose LangChain-specific model objects throughout the codebase.

Do not introduce LangGraph yet. Week 2 proves model/tool contracts independently before graph orchestration is added.

## Tool flow

```text
User
 ↓
LLM
 ↓
Tool Call
 ↓
Validate arguments
 ↓
Execute trusted tool
 ↓
Validate result
 ↓
Return evidence
 ↓
LLM response
```

## Golden prompts

At least 30:

```text
"Dataset có missing không?"
"Cho tôi schema."
"Cột nào có cardinality cao?"
"Có duplicate không?"
"Tóm tắt numeric columns."
```

## Prohibited

No:

```text
arbitrary Python
shell
automatic mutation
delete
unrestricted file access
```

## Deliverables

```text
src/llm/
src/tools/registry.py
evals/golden_tasks/tool_calling.json
```

## Metrics

```text
tool selection accuracy >= 90% preferred
argument validity >= 95%
execution success >= 95%
structured output validity >= 98%
```

If local hardware/model cannot reach target, record limitation rather than hiding it.

---

# WEEK 3 — AGENT SKILLS

## Goal

Move DS procedures out of one giant system prompt.

## Learn

```text
Agent Skills
SKILL.md
skill metadata
progressive disclosure
trigger design
references
scripts
assets
```

## Build first skills

```text
data-profiling
data-quality
leakage-analysis
```

## Skill content must specify

```text
purpose
when to use
when not to use
required evidence
tool sequence
interpretation rules
approval rules
expected output
```

## Example — leakage skill

Must ask:

```text
What is the target?
What is the prediction moment?
Would this feature exist at prediction time?
Is it derived from the outcome?
```

## Skill trigger evaluation

Should trigger:

```text
"Check this dataset."
"Profile this file."
"Find possible data-quality problems."
"Check for leakage."
```

Should not trigger:

```text
"Train XGBoost."
"Run a SQL query."
```

## Deliverables

```text
.agents/skills/
src/skills/registry.py
src/skills/loader.py
src/skills/selector.py
```

Skills remain framework-independent. LangGraph nodes will consume selected skill instructions from Week 4 onward.

## Pass

At least:

```text
3 production-quality skills
30 trigger/non-trigger tests
>= 90% skill selection accuracy
```

---

# WEEK 4 — LANGGRAPH SINGLE COPILOT + ROUTING + WORKFLOWS

## Goal

Build the first real Copilot.

Still ONE orchestrator, implemented as one compiled LangGraph `StateGraph`.

## Learn

```text
StateGraph
typed graph state
nodes and edges
conditional edges
reducers
subgraphs
checkpointers
thread_id
invoke / stream
recursion limits
```

## Build

```text
CopilotState
StateGraph builder
intake/context nodes
conditional router
workflow subgraphs
in-memory checkpointer
stop conditions
```

## LangGraph mapping

```text
User request
 ↓
intake_node
 ↓
context_node
 ↓
skill_selection_node
 ↓
route_node
 ├── direct_tool_node
 ├── profiling_subgraph
 ├── data_quality_subgraph
 ├── reasoning_node
 └── clarification_node
 ↓
response_node
 ↓
END
```

Use conditional edges for route selection. Do not ask the LLM to choose the order of deterministic steps inside a workflow.

## Initial workflows

```text
data_profiling
data_quality
```

## Routing policy

```text
known fixed procedure
→ workflow

open-ended analytical decision
→ LLM reasoning

single deterministic calculation
→ direct tool
```

## Example

```text
"Check data quality."
→ Data Quality Workflow
```

```text
"Should this column be removed?"
→ evidence + recommendation
→ no automatic removal
```

## State

Typed `CopilotState` tracks:

```text
messages_or_request
dataset
dataset_fingerprint
schema
target_if_known
selected_skill
selected_route
completed_workflows
warnings
current_task
tool_history
findings
evidence
artifacts
error_state
```

Compile with an in-memory checkpointer for development and always pass a `thread_id` from CLI/session boundaries.

Do NOT yet implement complex persistent memory or long-term user memory.

## Stop policy

```text
max workflow steps
max LLM calls
max retries
timeout
error budget
LangGraph recursion limit
```

## CLI V0

Commands:

```text
ds-copilot inspect data.csv
ds-copilot chat
ds-copilot quality data.xlsx
```

## Deliverables

```text
src/copilot/graph.py
src/copilot/state.py
src/copilot/nodes.py
src/copilot/router.py
src/workflows/profiling.py
src/workflows/data_quality.py
src/state/checkpointer.py
cli/main.py
```

## Pass

Copilot should solve 20 end-to-end profiling/quality tasks without the user naming tools.

Also verify:

```text
graph compiles successfully
route path matches expected nodes
same thread can continue state
separate thread IDs do not leak state
fixed workflows do not require the LLM to order steps
```

---

# WEEK 5 — DATA QUALITY + APPROVAL SYSTEM

## Goal

Automate most pre-modeling mechanical checks.

## Add tools

```text
detect_outliers()
detect_skewness()
detect_invalid_ranges()
detect_date_columns()
detect_possible_ids()
detect_class_imbalance()
detect_leakage_candidates()
detect_low_variance()
```

## Add approval architecture

Three action classes:

```text
READ_ONLY
RECOMMENDATION
MUTATION
```

## ApprovalRequest schema

```text
action
reason
evidence
affected_columns
expected_effect
risk
reversible
proposed_output
```

## LangGraph approval flow

```text
recommendation node
 ↓
approval node
 ↓
interrupt(ApprovalRequest)
 ↓
graph checkpoint saved
 ↓
human approves / rejects / modifies
 ↓
Command(resume=HumanDecision)
 ↓
approval-scope validation node
 ↓
approved? ── no → response / END
     │
    yes
     ↓
mutation node
 ↓
verification node
 ↓
decision-log node
```

Critical implementation rule:

```text
approval node contains no mutation side effects before interrupt()
mutation happens in a separate node after approval validation
nodes that may be replayed are idempotent
approval is bound to action + arguments + dataset fingerprint
```

Prompt instructions are not the security boundary. Approval enforcement remains in project-owned policy code; LangGraph only pauses and resumes the workflow.

## Leakage result

Never output only:

```text
"Column X is leakage."
```

Return:

```text
column
risk
reason
evidence
availability_at_prediction_time
questions_for_human
recommendation
human_confirmation_required
```

## Data Quality Report

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

## Synthetic validation dataset

Create controlled problems:

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

## Deliverables

```text
approval/
approval node + resume path
checkpointed data_quality subgraph
leakage skill
synthetic eval dataset
HITL graph tests
```

## Pass

```text
destructive action without approval = 0
known leakage-warning detection high enough for test set
source dataset never modified
```

---

# WEEK 6 — EDA + VISUALIZATION + STATISTICS

## Goal

Automate mechanical EDA while preserving human interpretation.

## Visualization tools

```text
plot_histogram()
plot_boxplot()
plot_bar()
plot_scatter()
plot_correlation()
plot_missingness()
plot_target_distribution()
```

## Statistical tools

```text
pearson()
spearman()
chi_square()
t_test()
mann_whitney()
anova()
normality_summary()
effect_size()
```

## Skills

```text
eda
statistical-analysis
```

## Workflow

Implement EDA and statistical analysis as separate LangGraph subgraphs with typed input/output state.

```text
Question
 ↓
Inspect variable types
 ↓
Choose valid method
 ↓
Check assumptions
 ↓
Execute tool
 ↓
Produce evidence
 ↓
Interpret conservatively
 ↓
State limitations
```

## Output schema

```text
question
method
why_this_method
assumptions
evidence
statistic
p_value_if_relevant
effect_size_if_relevant
interpretation
limitations
```

## Guardrails

Do not equate:

```text
correlation
=
causation
```

Do not report statistical significance without practical context when avoidable.

## Deliverables

```text
EDA subgraph
statistics subgraph
plot artifacts
node/subgraph tests
```

## Pass

Create a controlled statistics test set with known relationships and verify method selection + calculation.

---

# WEEK 7 — SAFE SQL + FILE/DATABASE UNIFICATION

## Goal

Support repetitive analytics over files and databases.

## SQL engine

```text
DuckDB
```

Load CSV/Parquet/Excel-derived tables when appropriate.

## Tools

```text
list_tables()
get_table_schema()
preview_table()
describe_table()
validate_sql()
execute_readonly_sql()
explain_sql()
```

## Policy

Allow:

```text
SELECT
WITH
EXPLAIN
```

Block:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
ATTACH unapproved sources
```

## NL2SQL subgraph

```text
Business Question
 ↓
Inspect schema
 ↓
Identify required tables/columns
 ↓
Generate SQL
 ↓
Static safety validation
 ↓
Execute
 ↓
Validate returned structure
 ↓
Explain result
```

The SQL validator and read-only executor remain trusted project tools. LangGraph routes and records the steps but does not replace SQL safety enforcement.

## SQL evaluation dataset

At least 40 tasks:

```text
filters
group-by
top-N
date aggregation
joins
CTEs
window functions
invalid columns
ambiguous questions
unsafe prompts
```

## Freight examples

```text
Top routes by shipment count
Average delay by carrier
On-time rate by month
Cost per shipment by route
Worst lanes by delay
```

## Metrics

```text
SQL execution accuracy
result correctness
schema grounding
unsafe SQL rate = 0
```

---

# WEEK 8 — PREPROCESSING + FEATURE ENGINEERING

## Goal

Reduce repetitive transformations without allowing silent changes.

## Tools — preprocessing

```text
propose_missing_strategy()
apply_imputation()
encode_one_hot()
encode_ordinal()
scale_standard()
scale_robust()
parse_dates()
cast_dtype()
```

## Tools — feature engineering

```text
create_date_parts()
create_ratio_feature()
create_log_transform()
create_group_aggregate()
create_interaction_candidate()
```

Feature engineering should be limited to interpretable, approved transforms in V1.

## LangGraph preprocessing subgraph

```text
Inspect
 ↓
Identify issue/opportunity
 ↓
Generate proposal
 ↓
Show evidence
 ↓
Human approves
 ↓
Create transformed COPY
 ↓
Validate
 ↓
Compare before/after
 ↓
Log decision
```

Use `interrupt()` at the approval node and resume only with a validated `HumanDecision`. The approved mutation executes in a later node and writes to a new dataset path.

## Critical rule

Always preserve:

```text
data/raw
```

Never mutate raw source.

Write to:

```text
data/interim
data/processed
```

## Skills

```text
preprocessing
feature-engineering
```

## Deliverables

```text
preprocessing tools
feature tools
approval integration
before/after validation report
```

## Pass

Every transformation must be reproducible from decision log + configuration.

---

# WEEK 9 — HUMAN-CONTROLLED BASELINE ML

## Goal

Automate baseline experimentation after DS decisions are confirmed.

## Copilot responsibilities

```text
inspect confirmed target
identify candidate problem type
show target distribution
recommend metrics
recommend split
check leakage state
suggest baseline candidates
run approved models
evaluate
compare
report
```

## Human responsibilities

```text
confirm target
confirm prediction moment
confirm problem formulation
confirm metric
confirm split
confirm features
approve models
choose final direction
```

## Baselines

Classification:

```text
DummyClassifier
LogisticRegression
RandomForestClassifier
XGBoost classifier
```

Regression:

```text
DummyRegressor
LinearRegression
RandomForestRegressor
XGBoost regressor
```

Do not use all automatically.

## LangGraph baseline-ML subgraph

```text
Confirmed Target
 ↓
Problem-Type Recommendation
 ↓
Leakage Review
 ↓
Split Recommendation
 ↓
Metric Recommendation
 ↓
HUMAN APPROVAL
 ↓
Build Preprocessor
 ↓
Train Baseline
 ↓
Evaluate
 ↓
Compare to Dummy
 ↓
Error Analysis
 ↓
Recommendation
```

Use explicit approval interrupts for target/problem formulation, split/metric/features and approved model list. A resume command must not bypass leakage review or approval-scope validation.

## Experiment metadata

Store:

```text
experiment_id
dataset fingerprint
target
features
split
preprocessing
model
hyperparameters
metrics
timestamp
decision references
artifact paths
```

## Deliverables

```text
baseline-modeling skill
model-evaluation skill
baseline workflow
experiment registry
```

## Pass

One classification and one regression end-to-end controlled test.

---

# WEEK 10 — SANDBOXED PYTHON + FILE OPERATIONS

## Goal

Add advanced flexibility without sacrificing the Safe Tool default.

## Sandbox use cases

Only when trusted tools are insufficient.

Examples:

```text
custom group analysis
one-off derived statistic
advanced plot
temporary transformation
custom error analysis
```

## Sandbox policy

Allowed:

```text
Python
approved libraries
project-scoped read
temporary workspace write
```

Blocked:

```text
network
shell
system directories
credential access
package installation
host file mutation
unbounded runtime
```

## Execution limits

```text
CPU/time limit
memory limit
file size limit
output size limit
max generated-code retries
```

## Generated code review

Flow:

```text
Need advanced analysis
 ↓
Generate code
 ↓
Policy scan
 ↓
Show planned operation if mutating
 ↓
Execute in sandbox
 ↓
Capture stdout/errors/artifacts
 ↓
Verify
 ↓
Return evidence
```

This flow can be represented as an advanced-analysis subgraph, but LangGraph is not the security sandbox. Policy scanning, filesystem permissions and isolated execution must remain separate enforcement layers.

## Project file editing

Implement approved:

```text
create report
create notebook helper file
create configuration
edit project documentation
save generated plot
save cleaned dataset
```

No deletion.

## Deliverables

```text
sandbox abstraction
filesystem permission layer
mutation approval integration
advanced-analysis subgraph
sandbox-node boundary tests
```

## Pass

Sandbox escape attempts and disallowed operations must fail in safety tests.

---

# WEEK 11 — FREIGHT/LOGISTICS SHOWCASE + NEW-TECH EXPERIMENT

## Goal

Prove utility on a realistic domain AND learn current agent technologies without compromising core architecture.

## Freight Skill

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

## Domain concepts

```text
shipment
carrier
lane
route
origin
destination
freight cost
transit time
ETA
actual delivery
on-time delivery
delay
distance
```

## KPIs

```text
On-Time Delivery Rate
Average Delay
Transit Time
Cost per Shipment
Cost per Distance
Carrier Performance
Route Performance
```

## End-to-end domain workflow

Build the freight showcase as a parent LangGraph subgraph that composes the already-tested core subgraphs. Do not duplicate profiling, quality, SQL, preprocessing or ML logic inside the domain skill.

```text
Shipment Dataset
 ↓
Profiling
 ↓
Data Quality
 ↓
Business/Target Discussion
 ↓
Human Confirmation
 ↓
EDA
 ↓
SQL Business Analysis
 ↓
Delay Analysis
 ↓
Leakage Review
 ↓
Human Approval
 ↓
Preprocessing
 ↓
Baseline Prediction
 ↓
Evaluation
 ↓
Business Summary
```

---

## MCP experiment

Build ONE useful MCP integration.

Examples:

```text
project metadata resource
experiment-results resource
read-only dataset catalog
```

Evaluate whether it improves:

```text
reuse
interoperability
tool exposure
architecture clarity
```

Do not migrate core tools solely for novelty.

---

## Multi-agent experiment

Create an experimental branch using specialist subgraphs or agent nodes:

```text
Root Copilot
├── SQL Specialist
└── ML Specialist
```

Compare against single-Copilot baseline.

Metrics:

```text
task success
latency
LLM calls
failure rate
maintainability
```

Decision:

```text
KEEP multi-agent
only if evidence shows material benefit.
```

This is a learning experiment, not a required final architecture.

Prefer a deterministic specialist subgraph when the task does not require an autonomous agent. Multi-agent routing must not weaken the shared permission and approval policies.

---

# WEEK 12 — EVALUATION, STREAMLIT, PORTFOLIO, OPTIONAL PERSISTENCE

## Goal

Turn the system into an evaluated, demonstrable product.

## Full evaluation set

Target:

```text
100–150 tasks
```

Suggested distribution:

```text
20 tool calls
15 skill selection
15 routing/workflow
20 data quality
15 EDA/statistics
20 SQL
20 preprocessing/HITL
20 ML
10 freight domain
10 safety/adversarial
```

Some tasks may belong to multiple categories.

## Metrics

```text
tool_selection_accuracy
tool_argument_accuracy
structured_output_validity
skill_selection_accuracy
workflow_completion_rate
SQL_execution_accuracy
unsafe_SQL_rate
approval_compliance
mutation_without_approval
unsupported_claim_rate
task_success_rate
average_LLM_calls
average_tool_calls
latency
```

Critical:

```text
mutation_without_approval = 0
unsafe_SQL_execution = 0
```

---

## Observability

Every run captures:

```text
run_id
thread_id
user_request
selected_skill
selected_workflow
graph_path
node_transitions
reasoning_decision_summary
tools_called
arguments
tool_outputs
recommendations
approval_requests
human_decisions
state_before
state_after
artifacts
errors
latency
checkpoint_reference
```

Do not store hidden chain-of-thought.

Store concise decision/routing summaries.

---

## Streamlit UI

Layout:

```text
┌──────────────────────────────────────────────────┐
│                 PERSONAL DS COPILOT              │
├──────────────────────────┬───────────────────────┤
│                          │ Project / Session     │
│          CHAT            │ Dataset              │
│                          │ Decisions            │
│                          │ Experiments          │
├──────────────────────────┴───────────────────────┤
│         Charts / Evidence / Reports              │
└──────────────────────────────────────────────────┘
```

Important response cards:

```text
Finding
Evidence
Recommendation
Human Decision Required
```

Streamlit invokes or streams the same compiled LangGraph used by the CLI. It must pass a stable `thread_id`, surface graph interrupts as approval cards and resume with a validated `Command(resume=...)`. UI code must not call mutation tools directly.

---

## Optional persistent state — only if core is stable

Implement simple local persistence:

```text
local SQLite checkpointer for graph/thread state
+
project_state.json or SQLite store for project facts
```

Persist:

```text
dataset references
confirmed target
approved decisions
completed workflows
experiments
artifact references
```

This is NOT long-term conversational memory.

Keep graph checkpoints separate from curated project state:

```text
checkpoint → execution continuity and HITL resume
project state → confirmed analytical decisions and artifact references
```

---

## Portfolio artifacts

Required:

```text
README.md
architecture diagram
evaluation_report.md
3 demo scenarios
screenshots
short demo video
human_ai_boundary.md
safety_model.md
```

---

# 9. THREE PORTFOLIO DEMOS

## DEMO 1 — Dataset Health Check

User:

```text
Analyze this shipment dataset before modeling.
```

Copilot:

```text
profiles
checks missing
checks duplicates
detects IDs
detects outliers
checks target balance
flags leakage candidates
generates report
```

No destructive modification.

---

## DEMO 2 — Business Analysis via SQL + EDA

User:

```text
Which carriers and routes have the worst delivery performance?
```

Flow:

```text
Freight skill
 ↓
Schema inspection
 ↓
SQL
 ↓
KPI calculation
 ↓
EDA
 ↓
Charts
 ↓
Evidence
 ↓
Business summary
```

---

## DEMO 3 — Human-Controlled Shipment Delay Baseline

User:

```text
I want to predict whether a shipment will arrive late.
```

Copilot must NOT train immediately.

It establishes:

```text
target
prediction moment
leakage
metric
split
features
```

with human confirmation.

Then:

```text
approved preprocessing
 ↓
baseline
 ↓
evaluation
 ↓
error analysis
 ↓
comparison
 ↓
report
```

This is the strongest portfolio demo.

---

# 10. EVALUATION IS CONTINUOUS

Do not wait for Week 12.

```text
W1 → tool correctness
W2 → tool calling
W3 → skill triggers
W4 → routing/workflows
W5 → data-quality detection + approval
W6 → analysis correctness
W7 → SQL safety
W8 → transformation reproducibility
W9 → ML workflow
W10 → sandbox/file safety
W11 → domain + architecture experiment
W12 → integrated benchmark
```

Rule:

> Every new capability ships with tests and at least one evaluation case.

---

# 11. DEVELOPMENT ROUTINE

Recommended:

```text
10–15 hours/week
```

Typical week:

```text
Day 1  — theory + design
Day 2  — implement core primitives
Day 3  — implement workflow
Day 4  — integrate
Day 5  — tests/evals
Day 6  — refactor + docs + demo
Day 7  — review/rest
```

For each feature:

```text
SPEC
 ↓
IMPLEMENT
 ↓
UNIT TEST
 ↓
INTEGRATION TEST
 ↓
EVAL
 ↓
DOCUMENT
```

---

# 12. CODE QUALITY RULES

## Rule 1

Business/DS logic must not live only inside prompts.

---

## Rule 2

LLM provider must be replaceable.

---

## Rule 3

All important outputs must have schemas.

---

## Rule 4

Raw data is immutable.

---

## Rule 5

Mutating actions require approval.

---

## Rule 6

Tools must be independently testable without LLM.

---

## Rule 7

Workflow must be independently understandable without LLM prompt.

---

## Rule 8

Skills encode procedure/knowledge, not low-level calculations.

---

## Rule 9

Every agent recommendation should reference evidence.

---

## Rule 10

Do not merge code you cannot explain.

---

# 13. WHAT AI CODING ASSISTANTS MAY HELP WITH

Allowed:

```text
boilerplate
unit-test skeleton
docstrings
type hints
refactoring suggestions
debugging
README formatting
```

You should personally understand:

```text
tool calling
structured output
skill loading
routing
workflows
state
approval policy
sandbox
SQL safety
evaluation
```

---

# 14. MILESTONES

## MILESTONE A — END WEEK 2

```text
Reliable DS tools
+
Local LLM
+
Structured output
+
Tool calling
```

Usable prototype:

```text
"Check missing values in this dataset."
```

---

## MILESTONE B — END WEEK 4

```text
Agent Skills
+
Single LangGraph Copilot
+
Typed graph state
+
Deterministic workflow subgraphs
+
CLI
```

First genuine Copilot version.

---

## MILESTONE C — END WEEK 6

```text
Data Quality
+
Leakage
+
EDA
+
Statistics
+
Human approval
```

Useful for real pre-modeling work.

---

## MILESTONE D — END WEEK 9

```text
Safe SQL
+
Preprocessing
+
Feature Engineering
+
Human-Controlled Baseline ML
```

Most core DS repetitive work covered.

---

## MILESTONE E — END WEEK 11

```text
Sandboxed Python
+
File operations
+
Freight Domain Skill
+
MCP experiment
+
Multi-agent experiment
```

Technology exploration without sacrificing core.

---

## MILESTONE F — END WEEK 12

```text
Evaluated
Local-first
Human-in-the-loop
Production-oriented
Personal Data Science Copilot
```

---

# 15. DEFINITION OF DONE

## Core runtime

- [ ] Runs local-first.
- [ ] Does not require paid OpenAI API.
- [ ] LLM provider abstraction exists.
- [ ] Structured outputs validated.
- [ ] Tool calling works.
- [ ] One compiled LangGraph `StateGraph` is the default orchestrator.
- [ ] Core tools and Skills remain testable without LangGraph.

## Tools

- [ ] At least 20 reliable tools.
- [ ] File loading supported.
- [ ] Data quality tools.
- [ ] EDA/statistical tools.
- [ ] Read-only SQL tools.
- [ ] Preprocessing tools.
- [ ] Feature-engineering tools.
- [ ] Baseline ML tools.

## Skills

- [ ] At least 8 high-quality skills.
- [ ] Skill selection evaluated.
- [ ] Freight domain skill exists.

## Workflow

- [ ] Profiling subgraph.
- [ ] Data-quality subgraph.
- [ ] EDA/statistics subgraphs.
- [ ] SQL subgraph.
- [ ] Preprocessing subgraph.
- [ ] Baseline ML subgraph.
- [ ] Conditional routes are tested against expected graph paths.

## Human control

- [ ] Approval schema.
- [ ] Approval UI/CLI.
- [ ] Mutation requires approval.
- [ ] Approval uses checkpointed `interrupt()` and validated resume input.
- [ ] Mutation runs in a separate node after approval validation.
- [ ] Decision log exists.
- [ ] Raw data never overwritten.

## Security

- [ ] SQL writes blocked.
- [ ] Arbitrary host Python blocked.
- [ ] Sandbox limits implemented.
- [ ] Filesystem scoped to project.
- [ ] Delete disabled.

## ML

- [ ] Human confirms target.
- [ ] Human confirms split.
- [ ] Human confirms main metric.
- [ ] Approved baseline can train.
- [ ] Dummy baseline included.
- [ ] Experiment metadata saved.

## Evaluation

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] Safety tests.
- [ ] Golden task set.
- [ ] Evaluation report.
- [ ] Mutation without approval = 0.
- [ ] Unsafe SQL execution = 0.
- [ ] Node, route, subgraph and resume-path tests.

## Product

- [ ] CLI.
- [ ] Streamlit UI.
- [ ] Architecture diagram.
- [ ] README.
- [ ] Three portfolio demos.
- [ ] Demo video.

## New technology

- [ ] LangGraph used only as the orchestration runtime.
- [ ] Typed state, conditional edges, subgraphs and checkpointer used.
- [ ] LangSmith remains optional rather than required for local V1.
- [ ] Agent Skills used.
- [ ] One MCP experiment completed.
- [ ] Multi-agent experiment evaluated.
- [ ] Multi-agent retained only if useful.

---

# 16. POST-V1 — DO AFTER THE 12-WEEK CORE

Only after V1 passes evaluation.

## V1.1 — Persistent Project Memory

```text
SQLite-backed graph checkpoints
resume project
remember confirmed decisions
restore experiment state
restore artifact catalog
```

Do not treat raw graph checkpoints as the only authoritative project memory. Persist curated decisions in project-owned schemas.

---

## V1.2 — PostgreSQL

```text
read-only connector
schema discovery
safe query execution
```

---

## V1.3 — Advanced experiment tracking

Possible:

```text
MLflow
```

---

## V1.4 — Explainability

```text
SHAP
feature importance
error slices
```

---

## V1.5 — Cloud fallback

Optional providers:

```text
Gemini
OpenAI
others
```

Only when local model is insufficient.

---

## V1.6 — Multi-agent expansion

Only if benchmark proves specialist agents improve outcomes.

---

# 17. WHAT NOT TO DO DURING THE 12 WEEKS

Avoid scope creep:

```text
do not build 10 agents
do not add vector DB without a real retrieval problem
do not build RAG just because it is popular
do not add Spark to small local data
do not build AutoML
do not build cloud deployment before local reliability
do not implement complex memory before state is reliable
do not migrate everything to MCP
do not optimize UI before workflows work
```

---

# 18. PORTFOLIO STORY

Do not say:

> "I built an AI Data Scientist that automatically does Data Science."

Use:

> "I built a local-first Personal Data Science Copilot designed to automate repetitive analytical workflows while keeping critical Data Science decisions under human control.
>
> The system uses LangGraph as a thin orchestration runtime over reusable Data Science tools, Agent Skills, deterministic workflow subgraphs, typed state, checkpointed approval gates and sandboxed code execution.
>
> It supports dataset profiling, data-quality analysis, EDA, statistics, safe SQL, approved preprocessing and feature engineering, and human-controlled baseline ML experimentation.
>
> I built a reproducible evaluation suite for tool use, workflow routing, SQL safety, approval compliance and task success. Freight and logistics is used as the primary domain showcase."

---

# 19. FINAL LEARNING ORDER

```text
PYTHON DS FUNCTIONS
        ↓
RELIABLE TOOLS
        ↓
LOCAL LLM
        ↓
STRUCTURED OUTPUT
        ↓
TOOL CALLING
        ↓
AGENT SKILLS
        ↓
LANGGRAPH FUNDAMENTALS
        ↓
TYPED STATE + NODES + EDGES
        ↓
SINGLE LANGGRAPH COPILOT
        ↓
DETERMINISTIC WORKFLOW SUBGRAPHS
        ↓
CHECKPOINTER + INTERRUPT APPROVAL
        ↓
EDA / STATS / SQL
        ↓
PREPROCESSING
        ↓
FEATURE ENGINEERING
        ↓
BASELINE ML
        ↓
SANDBOXED CODE
        ↓
DOMAIN SKILL
        ↓
MCP EXPERIMENT
        ↓
MULTI-AGENT EXPERIMENT
        ↓
EVALUATION
        ↓
STREAMLIT
        ↓
PERSISTENT PROJECT MEMORY LATER
```

---

# 20. ONE-SENTENCE ARCHITECTURE PRINCIPLE

> **Use deterministic software to execute repeatable Data Science work, use the LLM to understand intent and reason about ambiguous analytical choices, and require the Data Scientist to approve consequential data and modeling decisions.**

---

# 21. FINAL 12-WEEK VIEW

```text
WEEK 1
Reliable DS Tools
        ↓
WEEK 2
Local LLM + Structured Output + Tool Calling
        ↓
WEEK 3
Agent Skills
        ↓
WEEK 4
LangGraph Single Copilot + Typed State + Routing + Subgraphs + CLI
        ↓
WEEK 5
Data Quality + Leakage + Checkpointed Approval
        ↓
WEEK 6
EDA + Visualization + Statistics
        ↓
WEEK 7
Safe SQL + File/Database Analytics
        ↓
WEEK 8
Preprocessing + Feature Engineering
        ↓
WEEK 9
Human-Controlled Baseline ML
        ↓
WEEK 10
Sandboxed Python + Approved File Operations
        ↓
WEEK 11
Freight Domain Showcase + MCP + Multi-Agent Experiment
        ↓
WEEK 12
Full Evaluation + Streamlit + Portfolio
        ↓
V1.1
Persistent Cross-Session Project State
```

---

# 22. CURRENT TECHNOLOGY REFERENCES

Checked against current public documentation in September 2026:

- LangGraph orchestration, graph API, persistence and Human-in-the-Loop:
  - https://docs.langchain.com/oss/python/langgraph/overview
  - https://docs.langchain.com/oss/python/langgraph/graph-api
  - https://docs.langchain.com/oss/python/langgraph/persistence
  - https://docs.langchain.com/oss/python/langgraph/interrupts
  - https://docs.langchain.com/oss/python/langgraph/use-subgraphs

- Ollama integration for LangChain/LangGraph model nodes:
  - https://docs.langchain.com/oss/python/integrations/chat/ollama

- LangGraph testing; LangSmith remains optional:
  - https://docs.langchain.com/oss/python/langgraph/test
  - https://docs.langchain.com/langsmith/evaluate-graph

- Agent Skills specification:
  - https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx

- Ollama structured output / tool calling:
  - https://docs.ollama.com/capabilities/structured-outputs
  - https://docs.ollama.com/capabilities/tool-calling

- Model Context Protocol:
  - https://blog.modelcontextprotocol.io/posts/2026-07-28/
  - https://blog.modelcontextprotocol.io/posts/mcp-roadmap/

---

# FINAL PRODUCT

```text
              DATA SCIENTIST
                    │
                    ▼
          PERSONAL DS COPILOT
          LANGGRAPH ORCHESTRATOR
                    │
       ┌────────────┼─────────────┐
       │            │             │
     Skills      Workflows       Tools
       │            │             │
       └────────────┼─────────────┘
                    │
               Evidence
                    │
             Recommendation
                    │
              Human Decision
                    │
              Approved Action
                    │
                    ▼
          Results / Experiments
                    │
                    ▼
                Reports
```

**Success is not measured by how autonomous the Copilot is.**

Success is measured by:

```text
how much repetitive DS work it removes
+
how reliable its execution is
+
how well it preserves Data Scientist judgment
```
