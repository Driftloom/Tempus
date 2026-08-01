"""Email extractor for intelligence extraction."""


from structlog import get_logger

logger = get_logger(__name__)


class EmailExtractor:
    """Extractor for email intelligence."""

    def __init__(self):
        """Initialize email extractor."""
        self.deadline_keywords = ["deadline", "due by", "due date", "by", "before"]
        self.commitment_keywords = ["i will", "i'll", "promise", "commit", "agree"]
        self.action_keywords = ["please", "need to", "should", "must", "required"]

    async def extract(self, email: dict) -> dict:
        """Extract intelligence from email."""
        logger.info("Extracting email intelligence", email_id=email["id"])

        content = email.get("content", "").lower()

        extracted = {
            "deadlines": [],
            "commitments": [],
            "action_items": [],
            "important": False
        }

        # Extract deadlines
        deadlines = self._extract_deadlines(content, email["subject"])
        extracted["deadlines"] = deadlines

        # Extract commitments
        commitments = self._extract_commitments(content)
        extracted["commitments"] = commitments

        # Extract action items
        actions = self._extract_action_items(content)
        extracted["action_items"] = actions

        # Determine importance
        extracted["important"] = self._is_important(email, extracted)

        logger.info("Email extraction complete", email_id=email["id"], extracted=extracted)
        return extracted

    def _extract_deadlines(self, content: str, subject: str) -> list[dict]:
        """Extract deadlines from email content."""
        deadlines = []
        content_lower = content.lower()

        # Simple deadline extraction (would use NLP in production)
        for keyword in self.deadline_keywords:
            if keyword in content_lower:
                # Extract the sentence containing the keyword
                sentences = content_lower.split(".")
                for sentence in sentences:
                    if keyword in sentence:
                        deadlines.append({
                            "description": sentence.strip(),
                            "keyword": keyword
                        })

        return deadlines

    def _extract_commitments(self, content: str) -> list[str]:
        """Extract commitments from email content."""
        commitments = []
        content_lower = content.lower()

        for keyword in self.commitment_keywords:
            if keyword in content_lower:
                sentences = content_lower.split(".")
                for sentence in sentences:
                    if keyword in sentence:
                        commitments.append(sentence.strip())

        return commitments

    def _extract_action_items(self, content: str) -> list[str]:
        """Extract action items from email content."""
        actions = []
        content_lower = content.lower()

        for keyword in self.action_keywords:
            if keyword in content_lower:
                sentences = content_lower.split(".")
                for sentence in sentences:
                    if keyword in sentence:
                        actions.append(sentence.strip())

        return actions

    def _is_important(self, email: dict, extracted: dict) -> bool:
        """Determine if email is important."""
        # Important if has deadlines
        if extracted["deadlines"]:
            return True

        # Important if from certain senders
        important_senders = ["manager", "director", "ceo", "cto"]
        from_lower = email.get("from", "").lower()
        if any(sender in from_lower for sender in important_senders):
            return True

        # Important if subject contains urgency
        subject_lower = email.get("subject", "").lower()
        urgent_keywords = ["urgent", "important", "asap", "deadline"]
        if any(keyword in subject_lower for keyword in urgent_keywords):
            return True

        return False
