"""Unit tests for evals module."""

from unittest.mock import AsyncMock, patch

import pytest
from app.evals.framework import EvaluationFramework
from app.evals.metrics import EvaluationMetrics

from app.evals.runner import EvaluationRunner


@pytest.fixture
def eval_framework():
    """Create evaluation framework fixture."""
    return EvaluationFramework()


@pytest.fixture
def eval_metrics():
    """Create evaluation metrics fixture."""
    return EvaluationMetrics()


@pytest.fixture
def eval_runner():
    """Create evaluation runner fixture."""
    return EvaluationRunner()


# Evaluation Framework Tests
def test_eval_framework_initialization(eval_framework):
    """Test evaluation framework initialization."""
    assert eval_framework is not None
    assert len(eval_framework.evaluators) == 0


def test_eval_framework_register_evaluator(eval_framework):
    """Test registering an evaluator."""
    def test_evaluator(result, expected):
        return result == expected

    eval_framework.register_evaluator("test_evaluator", test_evaluator)

    assert "test_evaluator" in eval_framework.evaluators


def test_eval_framework_run_evaluation(eval_framework):
    """Test running evaluation."""
    def test_evaluator(result, expected):
        return result == expected

    eval_framework.register_evaluator("test_evaluator", test_evaluator)

    result = eval_framework.evaluate("test_evaluator", result="test", expected="test")

    assert result is True


def test_eval_framework_batch_evaluation(eval_framework):
    """Test batch evaluation."""
    def test_evaluator(result, expected):
        return result == expected

    eval_framework.register_evaluator("test_evaluator", test_evaluator)

    test_cases = [
        {"result": "test1", "expected": "test1"},
        {"result": "test2", "expected": "test2"},
    ]

    results = eval_framework.batch_evaluate("test_evaluator", test_cases)

    assert all(results)


# Evaluation Metrics Tests
def test_eval_metrics_accuracy(eval_metrics):
    """Test accuracy calculation."""
    predictions = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]

    accuracy = eval_metrics.accuracy(predictions, labels)

    assert 0 <= accuracy <= 1


def test_eval_metrics_precision(eval_metrics):
    """Test precision calculation."""
    predictions = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]

    precision = eval_metrics.precision(predictions, labels)

    assert 0 <= precision <= 1


def test_eval_metrics_recall(eval_metrics):
    """Test recall calculation."""
    predictions = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]

    recall = eval_metrics.recall(predictions, labels)

    assert 0 <= recall <= 1


def test_eval_metrics_f1_score(eval_metrics):
    """Test F1 score calculation."""
    predictions = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]

    f1 = eval_metrics.f1_score(predictions, labels)

    assert 0 <= f1 <= 1


def test_eval_metrics_confusion_matrix(eval_metrics):
    """Test confusion matrix calculation."""
    predictions = [1, 0, 1, 1, 0]
    labels = [1, 0, 1, 0, 0]

    cm = eval_metrics.confusion_matrix(predictions, labels)

    assert cm.shape == (2, 2)


# Evaluation Runner Tests
@pytest.mark.asyncio
async def test_eval_runner_run_test(eval_runner):
    """Test running a single test."""
    test_case = {
        "input": "test input",
        "expected_output": "test output",
        "evaluator": lambda x, y: x == y
    }

    with patch.object(eval_runner, '_execute_test', return_value={"passed": True}):
        result = await eval_runner.run_test(test_case)

        assert result["passed"] is True


@pytest.mark.asyncio
async def test_eval_runner_run_suite(eval_runner):
    """Test running a test suite."""
    test_suite = [
        {"input": "test1", "expected": "output1"},
        {"input": "test2", "expected": "output2"},
    ]

    with patch.object(eval_runner, 'run_test', new_callable=AsyncMock) as mock_run:
        mock_run.return_value = {"passed": True}

        results = await eval_runner.run_suite(test_suite)

        assert len(results) == 2


@pytest.mark.asyncio
async def test_eval_runner_generate_report(eval_runner):
    """Test generating evaluation report."""
    results = [
        {"test_id": "test1", "passed": True, "duration": 0.1},
        {"test_id": "test2", "passed": False, "duration": 0.2},
    ]

    report = eval_runner.generate_report(results)

    assert "summary" in report
    assert "passed" in report["summary"]
    assert "failed" in report["summary"]


def test_eval_runner_calculate_statistics(eval_runner):
    """Test calculating test statistics."""
    results = [
        {"passed": True, "duration": 0.1},
        {"passed": True, "duration": 0.2},
        {"passed": False, "duration": 0.3},
    ]

    stats = eval_runner.calculate_statistics(results)

    assert "total" in stats
    assert "passed" in stats
    assert "failed" in stats
    assert "pass_rate" in stats
