"""Email intelligence service."""

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.email.connectors.gmail_connector import GmailConnector
from app.email.connectors.outlook_connector import OutlookConnector
from app.email.extraction.email_extractor import EmailExtractor
from app.memory.service import MemoryService
from app.tasks.service import TaskService

logger = get_logger(__name__)


class EmailIntelligenceService:
    """Service for email intelligence and triage."""

    def __init__(
        self,
        gmail_connector: GmailConnector,
        outlook_connector: OutlookConnector,
        email_extractor: EmailExtractor,
        task_service: TaskService,
        memory_service: MemoryService
    ):
        """Initialize email intelligence service."""
        self.gmail_connector = gmail_connector
        self.outlook_connector = outlook_connector
        self.email_extractor = email_extractor
        self.task_service = task_service
        self.memory_service = memory_service

    async def sync_emails(
        self,
        db: AsyncSession,
        user_id: str,
        connector_type: str = "gmail",
        limit: int = 50
    ) -> dict:
        """Sync emails from connector and extract intelligence."""
        logger.info("Syncing emails", user_id=user_id, connector_type=connector_type)

        # Get connector
        if connector_type == "gmail":
            connector = self.gmail_connector
        elif connector_type == "outlook":
            connector = self.outlook_connector
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")

        # Fetch emails
        emails = await connector.fetch_emails(user_id, limit)

        # Process each email
        results = {
            "total": len(emails),
            "tasks_created": 0,
            "memories_created": 0,
            "errors": 0
        }

        for email in emails:
            try:
                # Extract intelligence
                extracted = await self.email_extractor.extract(email)

                # Create tasks if deadlines found
                if extracted.get("deadlines"):
                    for deadline in extracted["deadlines"]:
                        await self.task_service.create_from_nl(
                            db,
                            user_id,
                            deadline["description"],
                            source="email",
                            source_ref=email["id"]
                        )
                        results["tasks_created"] += 1

                # Create memory for important content
                if extracted.get("important"):
                    await self.memory_service.ingest(
                        db,
                        user_id,
                        email["content"],
                        source="email",
                        source_ref=email["id"],
                        tags=["external_untrusted:email"]
                    )
                    results["memories_created"] += 1

            except Exception as e:
                logger.error("Email processing failed", email_id=email["id"], error=str(e))
                results["errors"] += 1

        logger.info("Email sync completed", results=results)
        return results

    async def generate_digest(
        self,
        db: AsyncSession,
        user_id: str
    ) -> dict:
        """Generate daily email digest."""
        logger.info("Generating email digest", user_id=user_id)

        # Get recent tasks from email
        # Get recent memories from email

        digest = {
            "date": None,
            "summary": "Email digest",
            "tasks": [],
            "important_emails": []
        }

        return digest
