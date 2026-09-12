# Personal Data Science Copilot

Local-first project for learning reliable Data Science tools before adding
LLMs, LangGraph, agents, or tool-calling.

## Project Overview

The project builds a personal copilot from small, deterministic foundations.
Week 01 provides typed contracts, CSV/Excel/Parquet loaders, read-only
inspection tools, data-quality evidence, and descriptive summaries for tabular
data. The Data Scientist remains responsible for consequential interpretation
and decisions.

## Architecture Principle

Deterministic software should execute repeatable Data Science work. Later, an
LLM may help understand intent and discuss ambiguous choices, but Week 01 does
not include an LLM, agent, LangGraph graph, MCP, or tool-calling loop.

## Installation

Use Python 3.11 or newer and install the project with its development extras.

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
~~~

## Week 01

| Task | Scope | Status | Main files |
| --- | --- | --- | --- |
| W01-T01 | Repository and environment | Implemented | pyproject.toml, .gitignore |
| W01-T02 | Contracts and schemas | Implemented | src/tools/schemas.py, exceptions.py |
| W01-T03 | File loaders | Implemented | src/tools/loaders.py |
| W01-T04 | Inspection | Implemented | src/tools/inspection.py |
| W01-T05 | Data quality | Implemented | src/tools/quality.py, config.py |
| W01-T06 | Descriptive tools | Implemented | src/tools/descriptive.py |
| W01-T07 | Edge-case fixtures and tests | Implemented | tests/conftest.py, tests/unit/ |
| W01-T08 | Evaluation and documentation | Record added; runtime metrics pending | docs/week01_evaluation.md, docs/dev_journal.md |
| W01-T09 | File fingerprint | Planned | src/tools/fingerprint.py |

W01-T08 records evidence and known limitations. It does not add production
logic or start the W01-T09 fingerprint work.

## Running Tests and Checks

Run these commands from the project root after installation:

~~~powershell
python -m pytest tests/unit/test_loaders.py tests/unit/test_inspection.py tests/unit/test_quality.py tests/unit/test_descriptive.py -v
python -m pytest tests/unit/test_tool_schemas.py -v
python -m compileall -q src tests
ruff check src tests
mypy src tests
~~~

The first command is the main behavioral gate for the T03-T06 tool groups.
The schema command is the primary structured-output gate. T09 tests are not
part of the completed Week 01 scope.

## Example Usage

~~~python
from src.tools.loaders import load_dataset
from src.tools.inspection import preview_data
from src.tools.quality import check_missing

dataframe, load_result = load_dataset("data/sample.csv")
preview = preview_data(dataframe, max_rows=5)
missing_evidence = check_missing(dataframe)
~~~

load_dataset selects the CSV, Excel, or Parquet loader from the file extension.
check_missing returns structured missing-value evidence for each column. Both
operations are read-only; they do not overwrite the source file or mutate the
DataFrame.

## Safety and Immutability

- Raw files must never be overwritten by a Week 01 tool.
- Source DataFrames must remain unchanged.
- Quality tools report evidence; they do not drop rows, fill values, or delete
  columns.
- ID detection reports candidates only, never certainty.
- Rates are numeric values from 0.0 to 1.0.
- Structured results and errors are designed to be JSON-safe.

## Known Limitations

- Loaders currently support only CSV, Excel, and Parquet, and operate in
  memory rather than streaming large files.
- ID detection is evidence-based candidate detection, not proof of business
  identity.
- Descriptive statistics report evidence only. They do not recommend cleaning,
  feature engineering, or modeling actions.
- Non-finite descriptive statistics are normalized to None; pandas or NumPy
  may still emit a runtime warning while calculating them.
- Categorical values are stringified in structured descriptive output, so
  different source types can share the same serialized label.
- Some unhashable-value behaviors depend on the pandas runtime; portability
  tests document those cases where applicable.
- File fingerprinting, orchestration, LLM, UI, and ML features are outside
  the completed Week 01 scope.

## Evaluation

See docs/week01_evaluation.md for the evaluation definitions, commands,
robustness evidence, and current runtime status.

See docs/dev_journal.md for the short Week 01 development record.

## Roadmap

Complete the documented evaluation in a provisioned development environment,
then begin W01-T09 only after the Week 01 evidence and limitations remain
understood.
