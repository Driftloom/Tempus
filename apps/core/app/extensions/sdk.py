"""TEMPUS SDK for extension development."""

from abc import ABC, abstractmethod
from typing import Any

import httpx
import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class TempusClient:
    """TEMPUS API client for extensions."""

    def __init__(self, api_url: str, api_key: str):
        """Initialize TEMPUS client."""
        self.api_url = api_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=api_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        due_at: str | None = None
    ) -> dict[str, Any]:
        """Create a task."""
        response = await self.client.post(
            "/api/v1/tasks",
            json={
                "user_id": user_id,
                "title": title,
                "description": description,
                "priority": priority,
                "due_at": due_at,
            },
        )
        response.raise_for_status()
        return response.json()

    async def get_tasks(self, user_id: str, status: str | None = None) -> list[dict[str, Any]]:
        """Get tasks for user."""
        params = {"user_id": user_id}
        if status:
            params["status"] = status

        response = await self.client.get("/api/v1/tasks", params=params)
        response.raise_for_status()
        return response.json()

    async def create_memory(
        self,
        user_id: str,
        content: str,
        layer: str = "short_term",
        provenance: str = "extension"
    ) -> dict[str, Any]:
        """Create a memory."""
        response = await self.client.post(
            "/api/v1/memory",
            json={
                "user_id": user_id,
                "content": content,
                "layer": layer,
                "provenance": provenance,
            },
        )
        response.raise_for_status()
        return response.json()

    async def search_memory(self, user_id: str, query: str) -> list[dict[str, Any]]:
        """Search memory."""
        response = await self.client.get(
            "/api/v1/memory/search",
            params={"user_id": user_id, "query": query},
        )
        response.raise_for_status()
        return response.json()

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        priority: str = "medium"
    ) -> dict[str, Any]:
        """Create a notification."""
        response = await self.client.post(
            "/api/v1/notifications",
            json={
                "user_id": user_id,
                "title": title,
                "message": message,
                "priority": priority,
            },
        )
        response.raise_for_status()
        return response.json()


class ExtensionConfig(BaseModel):
    """Extension configuration."""
    name: str
    version: str
    description: str
    author: str
    permissions: list[str] = []
    capabilities: list[str] = []


class Extension(ABC):
    """Base class for TEMPUS extensions."""

    def __init__(self, config: ExtensionConfig, client: TempusClient):
        """Initialize extension."""
        self.config = config
        self.client = client

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize extension."""
        pass

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown extension."""
        pass

    async def handle_webhook(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle webhook event."""
        logger.info("Webhook received", extension=self.config.name, event_type=event_type)
        return {"status": "acknowledged"}


class ExtensionContext:
    """Context for extension execution."""

    def __init__(
        self,
        user_id: str,
        extension_id: str,
        metadata: dict[str, Any] | None = None
    ):
        """Initialize context."""
        self.user_id = user_id
        self.extension_id = extension_id
        self.metadata = metadata or {}

    def get_user_id(self) -> str:
        """Get user ID."""
        return self.user_id

    def get_extension_id(self) -> str:
        """Get extension ID."""
        return self.extension_id

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


class ExtensionRegistry:
    """Registry for managing extensions."""

    def __init__(self):
        """Initialize registry."""
        self._extensions: dict[str, Extension] = {}
        self._configs: dict[str, ExtensionConfig] = {}

    def register(self, extension: Extension) -> None:
        """Register an extension."""
        self._extensions[extension.config.name] = extension
        self._configs[extension.config.name] = extension.config
        logger.info("Extension registered", name=extension.config.name)

    def unregister(self, name: str) -> None:
        """Unregister an extension."""
        if name in self._extensions:
            del self._extensions[name]
            del self._configs[name]
            logger.info("Extension unregistered", name=name)

    def get(self, name: str) -> Extension | None:
        """Get extension by name."""
        return self._extensions.get(name)

    def get_config(self, name: str) -> ExtensionConfig | None:
        """Get extension config by name."""
        return self._configs.get(name)

    def list_extensions(self) -> list[ExtensionConfig]:
        """List all registered extensions."""
        return list(self._configs.values())

    async def initialize_all(self) -> None:
        """Initialize all registered extensions."""
        for extension in self._extensions.values():
            try:
                await extension.initialize()
                logger.info("Extension initialized", name=extension.config.name)
            except Exception as e:
                logger.error("Extension initialization failed", name=extension.config.name, error=str(e))

    async def shutdown_all(self) -> None:
        """Shutdown all registered extensions."""
        for extension in self._extensions.values():
            try:
                await extension.shutdown()
                logger.info("Extension shutdown", name=extension.config.name)
            except Exception as e:
                logger.error("Extension shutdown failed", name=extension.config.name, error=str(e))


# Global extension registry
extension_registry = ExtensionRegistry()
