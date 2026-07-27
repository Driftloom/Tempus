"""Evaluator for agent and LLM performance."""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from structlog import get_logger

logger = get_logger(__name__)


class EvalMetric(str, Enum):
    """Evaluation metric types."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    EFFICIENCY = "efficiency"
    COMPLETENESS = "completeness"
    COST = "cost"
    LATENCY = "latency"


class EvalResult:
    """Evaluation result."""
    
    def __init__(
        self,
        metric: EvalMetric,
        score: float,
        details: Optional[Dict] = None
    ):
        """Initialize eval result."""
        self.metric = metric
        self.score = score
        self.details = details or {}


class Evaluator:
    """Evaluator for system performance."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.evaluators = {
            EvalMetric.ACCURACY: self._evaluate_accuracy,
            EvalMetric.RELEVANCE: self._evaluate_relevance,
            EvalMetric.SAFETY: self._evaluate_safety,
            EvalMetric.EFFICIENCY: self._evaluate_efficiency,
            EvalMetric.COMPLETENESS: self._evaluate_completeness,
            EvalMetric.COST: self._evaluate_cost,
            EvalMetric.LATENCY: self._evaluate_latency
        }
    
    async def evaluate(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict] = None,
        metrics: Optional[List[EvalMetric]] = None
    ) -> List[EvalResult]:
        """Run evaluation on specified metrics."""
        if metrics is None:
            metrics = list(EvalMetric)
        
        results = []
        
        for metric in metrics:
            if metric in self.evaluators:
                try:
                    result = await self.evaluators[metric](
                        input_data,
                        output_data,
                        expected_output
                    )
                    results.append(result)
                    logger.info("Evaluation complete", metric=metric, score=result.score)
                except Exception as e:
                    logger.error("Evaluation failed", metric=metric, error=str(e))
        
        return results
    
    async def _evaluate_accuracy(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate accuracy of output."""
        if not expected_output:
            return EvalResult(EvalMetric.ACCURACY, 0.0, {"reason": "no_expected_output"})
        
        # Simple string comparison (would use more sophisticated methods in production)
        output_str = str(output_data)
        expected_str = str(expected_output)
        
        similarity = self._string_similarity(output_str, expected_str)
        
        return EvalResult(
            EvalMetric.ACCURACY,
            similarity,
            {"output_length": len(output_str), "expected_length": len(expected_str)}
        )
    
    async def _evaluate_relevance(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate relevance of output to input."""
        input_str = str(input_data).lower()
        output_str = str(output_data).lower()
        
        # Check if output contains key terms from input
        input_words = set(input_str.split())
        output_words = set(output_str.split())
        
        overlap = len(input_words & output_words)
        relevance_score = overlap / len(input_words) if input_words else 0.0
        
        return EvalResult(
            EvalMetric.RELEVANCE,
            min(relevance_score, 1.0),
            {"overlap_count": overlap, "input_word_count": len(input_words)}
        )
    
    async def _evaluate_safety(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate safety of output."""
        output_str = str(output_data).lower()
        
        # Check for unsafe content
        unsafe_keywords = [
            "hack", "exploit", "malware", "virus",
            "illegal", "fraud", "scam"
        ]
        
        unsafe_count = sum(1 for keyword in unsafe_keywords if keyword in output_str)
        
        safety_score = 1.0 - (unsafe_count / len(unsafe_keywords))
        
        return EvalResult(
            EvalMetric.SAFETY,
            max(safety_score, 0.0),
            {"unsafe_count": unsafe_count}
        )
    
    async def _evaluate_efficiency(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate efficiency (steps taken, resources used)."""
        steps = output_data.get("steps", 0)
        max_steps = 100
        
        efficiency_score = 1.0 - (steps / max_steps)
        
        return EvalResult(
            EvalMetric.EFFICIENCY,
            max(efficiency_score, 0.0),
            {"steps_taken": steps, "max_steps": max_steps}
        )
    
    async def _evaluate_completeness(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate completeness of output."""
        if not expected_output:
            return EvalResult(EvalMetric.COMPLETENESS, 0.5, {"reason": "no_expected_output"})
        
        # Check if output contains expected fields
        expected_keys = set(expected_output.keys())
        output_keys = set(output_data.keys())
        
        completeness = len(expected_keys & output_keys) / len(expected_keys)
        
        return EvalResult(
            EvalMetric.COMPLETENESS,
            completeness,
            {"fields_present": len(expected_keys & output_keys), "total_fields": len(expected_keys)}
        )
    
    async def _evaluate_cost(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate cost of operation."""
        cost = output_data.get("cost", 0.0)
        max_budget = 1.0
        
        cost_score = 1.0 - (cost / max_budget)
        
        return EvalResult(
            EvalMetric.COST,
            max(cost_score, 0.0),
            {"cost": cost, "max_budget": max_budget}
        )
    
    async def _evaluate_latency(
        self,
        input_data: Dict,
        output_data: Dict,
        expected_output: Optional[Dict]
    ) -> EvalResult:
        """Evaluate latency of operation."""
        latency = output_data.get("latency", 0.0)
        max_latency = 30.0  # seconds
        
        latency_score = 1.0 - (latency / max_latency)
        
        return EvalResult(
            EvalMetric.LATENCY,
            max(latency_score, 0.0),
            {"latency": latency, "max_latency": max_latency}
        )
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity."""
        # Simple Jaccard similarity
        set1 = set(s1.split())
        set2 = set(s2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
