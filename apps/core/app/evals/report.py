"""Report generator for eval results."""

from typing import Dict
from datetime import datetime
from structlog import get_logger

logger = get_logger(__name__)


class EvalReport:
    """Report generator for evaluation results."""
    
    def __init__(self):
        """Initialize report generator."""
    
    def generate_report(self, benchmark_results: Dict) -> str:
        """Generate markdown report from benchmark results."""
        report = []
        
        report.append("# Evaluation Report")
        report.append(f"\nGenerated: {datetime.utcnow().isoformat()}")
        
        # Summary
        report.append("\n## Summary")
        report.append(f"- Total Test Cases: {benchmark_results['total_cases']}")
        report.append(f"- Passed: {benchmark_results['passed']}")
        report.append(f"- Failed: {benchmark_results['failed']}")
        pass_rate = (benchmark_results['passed'] / benchmark_results['total_cases']) * 100
        report.append(f"- Pass Rate: {pass_rate:.1f}%")
        
        # Aggregate Scores
        report.append("\n## Aggregate Scores")
        for metric, score in benchmark_results['aggregate_scores'].items():
            report.append(f"- {metric}: {score:.3f}")
        
        # Detailed Results
        report.append("\n## Detailed Results")
        for result in benchmark_results['results']:
            test_case = result['test_case']
            report.append(f"\n### Test Case {test_case}")
            
            if 'error' in result:
                report.append(f"- Error: {result['error']}")
            else:
                avg_score = result.get('average_score', 0.0)
                report.append(f"- Average Score: {avg_score:.3f}")
                
                report.append("\n#### Evaluation Results")
                for eval_result in result['eval_results']:
                    metric = eval_result['metric']
                    score = eval_result['score']
                    report.append(f"- {metric}: {score:.3f}")
        
        return "\n".join(report)
    
    def save_report(self, report: str, filepath: str):
        """Save report to file."""
        with open(filepath, 'w') as f:
            f.write(report)
        logger.info("Report saved", filepath=filepath)
