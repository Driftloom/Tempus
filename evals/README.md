# TEMPUS Evaluation Framework

This directory contains evaluation datasets, test cases, and evaluation runners for TEMPUS.

## Structure
- `datasets/` - Golden datasets for regression testing
- `runners/` - Evaluation runner implementations
- `results/` - Evaluation results and reports

## Evaluation Metrics
The evals framework in `apps/core/app/evals/` supports:
- Accuracy
- Relevance  
- Safety
- Efficiency
- Completeness
- Cost
- Latency

## Usage
Run evaluations using the benchmark runner:
```python
from app.evals.benchmark import Benchmark
from app.evals.evaluator import Evaluator

evaluator = Evaluator()
benchmark = Benchmark(evaluator)
benchmark.add_test_case(input_data, expected_output)
results = await benchmark.run_benchmark(system_under_test)
```
