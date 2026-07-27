"""Benchmark runner for evals."""

from typing import Dict, List
from app.evals.evaluator import Evaluator, EvalMetric
from structlog import get_logger

logger = get_logger(__name__)


class Benchmark:
    """Benchmark for running evals on test cases."""
    
    def __init__(self, evaluator: Evaluator):
        """Initialize benchmark."""
        self.evaluator = evaluator
        self.test_cases = []
    
    def add_test_case(
        self,
        input_data: Dict,
        expected_output: Dict,
        metadata: Optional[Dict] = None
    ):
        """Add a test case."""
        self.test_cases.append({
            "input": input_data,
            "expected": expected_output,
            "metadata": metadata or {}
        })
    
    async def run_benchmark(
        self,
        system_under_test,
        metrics: Optional[List[EvalMetric]] = None
    ) -> Dict:
        """Run benchmark on all test cases."""
        logger.info("Running benchmark", test_cases=len(self.test_cases))
        
        results = {
            "total_cases": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "results": [],
            "aggregate_scores": {}
        }
        
        for i, test_case in enumerate(self.test_cases):
            try:
                # Run system under test
                output = await system_under_test(test_case["input"])
                
                # Evaluate
                eval_results = await self.evaluator.evaluate(
                    test_case["input"],
                    output,
                    test_case["expected"],
                    metrics
                )
                
                # Calculate average score
                avg_score = sum(r.score for r in eval_results) / len(eval_results) if eval_results else 0.0
                
                if avg_score >= 0.7:  # 70% threshold
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                
                results["results"].append({
                    "test_case": i,
                    "input": test_case["input"],
                    "output": output,
                    "expected": test_case["expected"],
                    "eval_results": [r.__dict__ for r in eval_results],
                    "average_score": avg_score
                })
                
                # Update aggregate scores
                for eval_result in eval_results:
                    metric = eval_result.metric.value
                    if metric not in results["aggregate_scores"]:
                        results["aggregate_scores"][metric] = []
                    results["aggregate_scores"][metric].append(eval_result.score)
                
            except Exception as e:
                logger.error("Test case failed", test_case=i, error=str(e))
                results["failed"] += 1
                results["results"].append({
                    "test_case": i,
                    "error": str(e)
                })
        
        # Calculate final aggregate scores
        for metric, scores in results["aggregate_scores"].items():
            results["aggregate_scores"][metric] = sum(scores) / len(scores)
        
        logger.info("Benchmark complete", passed=results["passed"], failed=results["failed"])
        return results
