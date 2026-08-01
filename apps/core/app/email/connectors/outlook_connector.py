"""Outlook connector for email intelligence."""


import httpx
from structlog import get_logger

logger = get_logger(__name__)


class OutlookConnector:
    """Connector for Microsoft Graph API (Outlook)."""

    def __init__(self, access_token: str | None = None):
        """Initialize Outlook connector."""
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0/me"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_emails(
        self,
        user_id: str,
        limit: int = 50,
        folder: str = "inbox"
    ) -> list[dict]:
        """Fetch recent emails from Outlook via Microsoft Graph API."""
        logger.info("Fetching Outlook emails", user_id=user_id, limit=limit, folder=folder)

        if not self.access_token:
            logger.warning("No access token provided, returning empty list")
            return []

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            params = {
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,receivedDateTime,body"
            }

            # Fetch messages from specified folder
            response = await self.client.get(
                f"{self.base_url}/mailFolders/{folder}/messages",
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                logger.error("Outlook API error", status_code=response.status_code, response=response.text)
                return []

            data = response.json()
            messages = data.get("value", [])

            # Parse messages
            emails = []
            for message in messages:
                email_data = self._parse_message(message)
                if email_data:
                    emails.append(email_data)

            logger.info("Outlook emails fetched successfully", count=len(emails))
            return emails

        except Exception as e:
            logger.error("Failed to fetch Outlook emails", error=str(e))
            return []

    def _parse_message(self, message: dict) -> dict | None:
        """Parse Microsoft Graph message to standard format."""
        try:
            from_data = message.get("from", {}).get("emailAddress", {})

            return {
                "id": message.get("id"),
                "subject": message.get("subject", "(No Subject)"),
                "from": from_data.get("address", "Unknown"),
                "content": self._extract_body(message.get("body", {})),
                "date": message.get("receivedDateTime", "")
            }
        except Exception as e:
            logger.error("Failed to parse message", error=str(e))
            return None

    def _extract_body(self, body: dict) -> str:
        """Extract email body from Graph API body object."""
        content_type = body.get("contentType", "text")
        content = body.get("content", "")

        if content_type == "html":
            # In production, would strip HTML tags
            import re
            clean_text = re.sub(r'<[^>]+>', '', content)
            return clean_text

        return content

    async def authenticate(self, access_token: str, refresh_token: str | None = None) -> dict:
        """Set authentication tokens."""
        self.access_token = access_token
        logger.info("Outlook connector authenticated")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "authenticated": True
        }

    async def refresh_access_token(self, refresh_token: str) -> str | None:
        """Refresh access token using refresh token."""
        # This would call the OAuth2 handler to refresh the token
        logger.info("Refreshing Outlook access token")
        return self.access_token

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.info("Outlook connector closed")
