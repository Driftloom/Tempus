"""Extensions package for plugin architecture."""

from app.extensions.sdk import (
    TempusClient,
    ExtensionConfig,
    Extension,
    ExtensionContext,
    ExtensionRegistry,
    extension_registry,
)
from app.extensions.plugin import (
    PluginManager,
    PluginValidator,
    PluginPermissions,
)
from app.extensions.webhooks import (
    WebhookHandler,
    WebhookValidator,
    WEBHOOK_SCHEMES,
)

__all__ = [
    "TempusClient",
    "ExtensionConfig",
    "Extension",
    "ExtensionContext",
    "ExtensionRegistry",
    "extension_registry",
    "PluginManager",
    "PluginValidator",
    "PluginPermissions",
    "WebhookHandler",
    "WebhookValidator",
    "WEBHOOK_SCHEMES",
]
