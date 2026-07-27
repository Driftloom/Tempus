"""Unit tests for task service."""

import pytest
from app.tasks.nlp.nl_parser import NLParser
from app.tasks.priority.priority_scorer import PriorityScorer
from app.database.models.task import TaskPriority


@pytest.fixture
def nl_parser():
    """Fixture for NL parser."""
    return NLParser()


@pytest.fixture
def priority_scorer():
    """Fixture for priority scorer."""
    return PriorityScorer()


class TestNLParser:
    """Tests for natural language parser."""
    
    def test_parse_simple_task(self, nl_parser):
        """Test parsing simple task."""
        result = nl_parser.parse("Complete the project")
        assert result["title"] == "Complete the project"
    
    def test_parse_task_with_date(self, nl_parser):
        """Test parsing task with date."""
        result = nl_parser.parse("Complete the project by tomorrow")
        assert "due_at" in result
    
    def test_parse_task_with_time_estimate(self, nl_parser):
        """Test parsing task with time estimate."""
        result = nl_parser.parse("Complete the project 30 min")
        assert result["estimated_minutes"] == 30
    
    def test_parse_task_with_tags(self, nl_parser):
        """Test parsing task with tags."""
        result = nl_parser.parse("Complete the project #urgent #work")
        assert "urgent" in result["tags"]
        assert "work" in result["tags"]


class TestPriorityScorer:
    """Tests for priority scorer."""
    
    def test_score_urgent_task(self, priority_scorer):
        """Test scoring urgent task."""
        parsed = {"title": "urgent task", "tags": ["urgent"]}
        priority = priority_scorer.score(parsed)
        assert priority == TaskPriority.URGENT
    
    def test_score_normal_task(self, priority_scorer):
        """Test scoring normal task."""
        parsed = {"title": "normal task", "tags": []}
        priority = priority_scorer.score(parsed)
        assert priority == TaskPriority.LOW
    
    def test_score_important_task(self, priority_scorer):
        """Test scoring important task."""
        parsed = {"title": "important task", "tags": ["important"]}
        priority = priority_scorer.score(parsed)
        assert priority == TaskPriority.HIGH
