"""Unit tests for tasks module."""

from unittest.mock import AsyncMock, patch

import pytest

from app.tasks.nlp.nl_parser import NLPParser
from app.tasks.priority.priority_scorer import PriorityScorer
from app.tasks.scheduling.scheduler import TaskScheduler
from app.tasks.service import TaskService


@pytest.fixture
def task_service():
    """Create task service fixture."""
    with patch('app.tasks.service.task_repository') as mock_repo:
        return TaskService(mock_repo)


@pytest.fixture
def task_scheduler():
    """Create task scheduler fixture."""
    return TaskScheduler()


@pytest.fixture
def priority_scorer():
    """Create priority scorer fixture."""
    return PriorityScorer()


@pytest.fixture
def nlp_parser():
    """Create NLP parser fixture."""
    return NLPParser()


# Task Service Tests
@pytest.mark.asyncio
async def test_task_service_create_task(task_service):
    """Test task creation."""
    task_data = {"title": "Test Task", "description": "Test description"}

    with patch.object(task_service.task_repo, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = {"id": "task1", **task_data}

        result = await task_service.create_task("user123", task_data)

        assert result["title"] == "Test Task"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_task_service_get_task(task_service):
    """Test task retrieval."""
    with patch.object(task_service.task_repo, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"id": "task1", "title": "Test Task"}

        result = await task_service.get_task("task1")

        assert result["id"] == "task1"


@pytest.mark.asyncio
async def test_task_service_update_task(task_service):
    """Test task update."""
    update_data = {"title": "Updated Task"}

    with patch.object(task_service.task_repo, 'update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = {"id": "task1", **update_data}

        result = await task_service.update_task("task1", update_data)

        assert result["title"] == "Updated Task"


@pytest.mark.asyncio
async def test_task_service_delete_task(task_service):
    """Test task deletion."""
    with patch.object(task_service.task_repo, 'delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True

        result = await task_service.delete_task("task1")

        assert result is True


@pytest.mark.asyncio
async def test_task_service_list_tasks(task_service):
    """Test task listing."""
    with patch.object(task_service.task_repo, 'list', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [
            {"id": "task1", "title": "Task 1"},
            {"id": "task2", "title": "Task 2"},
        ]

        result = await task_service.list_tasks("user123")

        assert len(result) == 2


# Task Scheduler Tests
def test_task_scheduler_schedule_task(task_scheduler):
    """Test scheduling a task."""
    task = {"id": "task1", "scheduled_time": "2024-01-01T10:00:00Z"}

    task_scheduler.schedule(task)

    assert "task1" in task_scheduler.scheduled_tasks


def test_task_scheduler_unschedule_task(task_scheduler):
    """Test unscheduling a task."""
    task = {"id": "task1", "scheduled_time": "2024-01-01T10:00:00Z"}
    task_scheduler.schedule(task)
    task_scheduler.unschedule("task1")

    assert "task1" not in task_scheduler.scheduled_tasks


def test_task_scheduler_get_due_tasks(task_scheduler):
    """Test getting due tasks."""
    from datetime import datetime, timedelta

    # Add a past-due task
    past_time = datetime.utcnow() - timedelta(hours=1)
    task = {"id": "task1", "scheduled_time": past_time.isoformat()}
    task_scheduler.schedule(task)

    due_tasks = task_scheduler.get_due_tasks()

    assert len(due_tasks) >= 1


# Priority Scorer Tests
def test_priority_scorer_score_high_priority(priority_scorer):
    """Test scoring high priority task."""
    task = {"title": "URGENT: Fix critical bug", "due_date": "2024-01-01"}
    score = priority_scorer.score(task)

    assert score >= 0.8


def test_priority_scorer_score_low_priority(priority_scorer):
    """Test scoring low priority task."""
    task = {"title": "Optional: Read documentation", "due_date": None}
    score = priority_scorer.score(task)

    assert score < 0.5


def test_priority_scorer_score_with_deadline(priority_scorer):
    """Test scoring with deadline proximity."""
    from datetime import datetime, timedelta

    # Task due soon
    soon = datetime.utcnow() + timedelta(hours=2)
    task = {"title": "Task due soon", "due_date": soon.isoformat()}
    score = priority_scorer.score(task)

    assert score >= 0.7


# NLP Parser Tests
def test_nlp_parser_extract_task(nlp_parser):
    """Test extracting task from natural language."""
    text = "I need to finish the report by Friday"
    task = nlp_parser.extract_task(text)

    assert "finish" in task["title"].lower() or "report" in task["title"].lower()


def test_nlp_parser_extract_deadline(nlp_parser):
    """Test extracting deadline from text."""
    text = "Complete the project by next Monday"
    task = nlp_parser.extract_task(text)

    assert task.get("due_date") is not None


def test_nlp_parser_extract_priority(nlp_parser):
    """Test extracting priority from text."""
    text = "URGENT: Fix the critical bug immediately"
    task = nlp_parser.extract_task(text)

    assert task.get("priority") == "high"


def test_nlp_parser_extract_multiple_tasks(nlp_parser):
    """Test extracting multiple tasks."""
    text = "I need to: 1) Write code, 2) Test it, 3) Deploy it"
    tasks = nlp_parser.extract_tasks(text)

    assert len(tasks) >= 2


def test_nlp_parser_parse_complex_sentence(nlp_parser):
    """Test parsing complex sentence."""
    text = "After meeting with the team, I should update the documentation and send the email"
    tasks = nlp_parser.extract_tasks(text)

    assert len(tasks) >= 1
