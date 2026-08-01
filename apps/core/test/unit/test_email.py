"""Unit tests for email module."""

from unittest.mock import patch

import pytest
from app.email.models import EmailMessage, EmailMetadata
from app.email.processor import EmailProcessor


@pytest.fixture
def email_processor():
    """Create email processor fixture."""
    with patch('app.email.processor.task_repository') as mock_repo:
        return EmailProcessor(mock_repo)


@pytest.fixture
def email_message():
    """Create email message fixture."""
    return EmailMessage(
        id="email1",
        user_id="user123",
        subject="Meeting tomorrow at 3PM",
        body="Don't forget the meeting with the team",
        sender="colleague@example.com",
        timestamp="2024-01-01T10:00:00Z"
    )


# Email Processor Tests
@pytest.mark.asyncio
async def test_email_processor_process(email_processor, email_message):
    """Test email processing."""
    with patch.object(email_processor, '_extract_tasks', return_value=[{"title": "Meeting at 3PM"}]):
        with patch.object(email_processor, '_extract_deadlines', return_value=["2024-01-02T15:00:00Z"]):
            result = await email_processor.process(email_message)

            assert "tasks" in result
            assert len(result["tasks"]) >= 1


@pytest.mark.asyncio
async def test_email_processor_extract_tasks(email_processor):
    """Test task extraction from email."""
    email_text = "You need to: 1) Finish the report, 2) Call the client, 3) Send the invoice"

    tasks = email_processor._extract_tasks(email_text)

    assert len(tasks) >= 2


@pytest.mark.asyncio
async def test_email_processor_extract_deadlines(email_processor):
    """Test deadline extraction from email."""
    email_text = "The project is due next Friday and the meeting is tomorrow at 3PM"

    deadlines = email_processor._extract_deadlines(email_text)

    assert len(deadlines) >= 1


@pytest.mark.asyncio
async def test_email_processor_extract_commitments(email_processor):
    """Test commitment extraction from email."""
    email_text = "I promise to deliver the report by Friday and I'll call you tomorrow"

    commitments = email_processor._extract_commitments(email_text)

    assert len(commitments) >= 1


@pytest.mark.asyncio
async def test_email_processor_prioritize(email_processor):
    """Test email prioritization."""
    urgent_email = EmailMessage(
        id="email1",
        user_id="user123",
        subject="URGENT: Server down",
        body="Production server is down",
        sender="alerts@example.com"
    )

    priority = email_processor.prioritize(urgent_email)

    assert priority == "high"


@pytest.mark.asyncio
async def test_email_processor_classify(email_processor):
    """Test email classification."""
    work_email = EmailMessage(
        id="email1",
        user_id="user123",
        subject="Project update",
        body="Here is the project status",
        sender="manager@example.com"
    )

    classification = email_processor.classify(work_email)

    assert classification in ["work", "personal", "promotional", "social"]


# Email Model Tests
def test_email_message_initialization(email_message):
    """Test email message initialization."""
    assert email_message.id == "email1"
    assert email_message.user_id == "user123"
    assert email_message.subject == "Meeting tomorrow at 3PM"


def test_email_metadata_initialization():
    """Test email metadata initialization."""
    metadata = EmailMetadata(
        email_id="email1",
        priority="high",
        category="work",
        has_deadline=True,
        has_commitment=True
    )

    assert metadata.email_id == "email1"
    assert metadata.priority == "high"
    assert metadata.has_deadline is True


def test_email_message_with_attachments():
    """Test email message with attachments."""
    email = EmailMessage(
        id="email1",
        user_id="user123",
        subject="Report attached",
        body="Please find the report attached",
        attachments=["report.pdf", "data.xlsx"]
    )

    assert len(email.attachments) == 2
    assert "report.pdf" in email.attachments


def test_email_message_thread_id():
    """Test email message with thread ID."""
    email = EmailMessage(
        id="email1",
        user_id="user123",
        subject="Re: Project update",
        body="Thanks for the update",
        thread_id="thread123"
    )

    assert email.thread_id == "thread123"
