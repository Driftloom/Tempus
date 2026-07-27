"""Webhook handling for extensions."""

from typing import Dict, Any, Callable, Optional
from fastapi import Request, HTTPException
from app.extensions.sdk import ExtensionRegistry
import structlog

logger = structlog.get_logger(__name__)


class WebhookHandler:
    """Handle webhook events for extensions."""

    def __init__(self, registry: ExtensionRegistry):
        """Initialize webhook handler."""
        self.registry = registry
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register a webhook handler."""
        self._handlers[event_type] = handler
        logger.info("Webhook handler registered", event_type=event_type)

    async def handle_webhook(
        self,
        extension_name: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle webhook event for extension."""
        extension = self.registry.get(extension_name)
        if not extension:
            raise HTTPException(status_code=404, detail="Extension not found")

        try:
            result = await extension.handle_webhook(event_type, payload)
            logger.info("Webhook handled", extension=extension_name, event_type=event_type)
            return result
        except Exception as e:
            logger.error("Webhook handling failed", extension=extension_name, error=str(e))
            raise HTTPException(status_code=500, detail="Webhook handling failed")

    async def broadcast_webhook(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast webhook to all extensions with webhook permission."""
        results = {}
        
        for config in self.registry.list_extensions():
            if "webhook" in config.permissions:
                try:
                    extension = self.registry.get(config.name)
                    result = await extension.handle_webhook(event_type, payload)
                    results[config.name] = result
                except Exception as e:
                    logger.error("Webhook broadcast failed", extension=config.name, error=str(e))
                    results[config.name] = {"status": "error", "error": str(e)}
        
        return {"results": results}


class WebhookValidator:
    """Validate webhook payloads."""

    @staticmethod
    def validate_payload(payload: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate webhook payload against schema."""
        errors = []
        
        for field, field_type in schema.items():
            if field not in payload:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(payload[field], field_type):
                errors.append(f"Field {field} has wrong type")
        
        return len(errors) == 0, errors


# Common webhook event schemas
WEBHOOK_SCHEMAS = {
    "task.created": {"user_id": str, "task_id": str, "title": str},
    "task.completed": {"user_id": str, "task_id": str},
    "memory.created": {"user_id": str, "memory_id": str, "content": str},
    "notification.created": {"user_id": str, "notification_id": str, "title": str},
}
