"""Gmail connector for email intelligence."""


import httpx
from structlog import get_logger

logger = get_logger(__name__)


class GmailConnector:
    """Connector for Gmail API with OAuth2 integration."""

    def __init__(self, access_token: str | None = None):
        """Initialize Gmail connector."""
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/gmail/v1/users/me"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_emails(
        self,
        user_id: str,
        limit: int = 50,
        query: str = "is:inbox"
    ) -> list[dict]:
        """Fetch recent emails from Gmail."""
        logger.info("Fetching Gmail emails", user_id=user_id, limit=limit, query=query)

        if not self.access_token:
            logger.warning("No access token provided, returning empty list")
            return []

        try:
            # Fetch message list
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            params = {
                "maxResults": limit,
                "q": query
            }

            response = await self.client.get(
                f"{self.base_url}/messages",
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                logger.error("Gmail API error", status_code=response.status_code, response=response.text)
                return []

            data = response.json()
            messages = data.get("messages", [])

            # Fetch full message details for each
            emails = []
            for message in messages[:limit]:
                email_data = await self._fetch_message_detail(message["id"], headers)
                if email_data:
                    emails.append(email_data)

            logger.info("Gmail emails fetched successfully", count=len(emails))
            return emails

        except Exception as e:
            logger.error("Failed to fetch Gmail emails", error=str(e))
            return []

    async def _fetch_message_detail(self, message_id: str, headers: dict) -> dict | None:
        """Fetch detailed message content."""
        try:
            response = await self.client.get(
                f"{self.base_url}/messages/{message_id}",
                headers=headers,
                params={"format": "full"}
            )

            if response.status_code != 200:
                logger.error("Failed to fetch message detail", message_id=message_id)
                return None

            data = response.json()
            payload = data.get("payload", {})
            headers_data = payload.get("headers", [])

            # Extract headers
            subject = self._get_header(headers_data, "Subject")
            from_email = self._get_header(headers_data, "From")
            date = self._get_header(headers_data, "Date")

            # Extract body
            body = self._extract_body(payload)

            return {
                "id": message_id,
                "subject": subject or "(No Subject)",
                "from": from_email or "Unknown",
                "content": body or "",
                "date": date or ""
            }

        except Exception as e:
            logger.error("Failed to parse message detail", message_id=message_id, error=str(e))
            return None

    def _get_header(self, headers: list[dict], name: str) -> str | None:
        """Extract header value by name."""
        for header in headers:
            if header.get("name") == name:
                return header.get("value")
        return None

    def _extract_body(self, payload: dict) -> str:
        """Extract email body from payload."""
        body = ""

        # Try to get body from payload
        if "body" in payload and payload["body"].get("data"):
            import base64
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

        # If multipart, extract from parts
        elif "parts" in payload:
            for part in payload["parts"]:
                if "body" in part and part["body"].get("data"):
                    import base64
                    body += base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                elif "parts" in part:
                    # Recursively extract from nested parts
                    body += self._extract_body(part)

        return body

    async def authenticate(self, access_token: str, refresh_token: str | None = None) -> dict:
        """Set authentication tokens."""
        self.access_token = access_token
        logger.info("Gmail connector authenticated")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "authenticated": True
        }

    async def refresh_access_token(self, refresh_token: str) -> str | None:
        """Refresh access token using refresh token."""
        # This would call the OAuth2 handler to refresh the token
        # For now, return the existing token
        logger.info("Refreshing Gmail access token")
        return self.access_token

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        logger.info("Gmail connector closed")
