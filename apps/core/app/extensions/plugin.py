"""Plugin architecture for dynamic extension loading."""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.extensions.sdk import Extension, ExtensionConfig, ExtensionRegistry
import structlog

logger = structlog.get_logger(__name__)


class PluginManager:
    """Manager for loading and managing plugins."""

    def __init__(self, registry: ExtensionRegistry):
        """Initialize plugin manager."""
        self.registry = registry
        self._loaded_plugins: Dict[str, Any] = {}

    async def load_plugin(self, plugin_path: str) -> bool:
        """Load a plugin from file path."""
        try:
            path = Path(plugin_path)
            if not path.exists():
                logger.error("Plugin path does not exist", path=plugin_path)
                return False

            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if spec is None or spec.loader is None:
                logger.error("Failed to load plugin spec", path=plugin_path)
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules["plugin"] = module
            spec.loader.exec_module(module)

            # Look for extension class
            if hasattr(module, "create_extension"):
                extension = module.create_extension()
                self.registry.register(extension)
                self._loaded_plugins[plugin_path] = module
                logger.info("Plugin loaded successfully", path=plugin_path)
                return True
            else:
                logger.error("Plugin missing create_extension function", path=plugin_path)
                return False

        except Exception as e:
            logger.error("Plugin loading failed", path=plugin_path, error=str(e))
            return False

    async def unload_plugin(self, plugin_path: str) -> bool:
        """Unload a plugin."""
        try:
            if plugin_path in self._loaded_plugins:
                module = self._loaded_plugins[plugin_path]
                
                # Unregister extension if exists
                if hasattr(module, "create_extension"):
                    extension = module.create_extension()
                    self.registry.unregister(extension.config.name)
                
                del self._loaded_plugins[plugin_path]
                logger.info("Plugin unloaded", path=plugin_path)
                return True
            
            return False

        except Exception as e:
            logger.error("Plugin unloading failed", path=plugin_path, error=str(e))
            return False

    async def load_plugins_from_directory(self, directory: str) -> int:
        """Load all plugins from a directory."""
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.warning("Plugin directory does not exist", directory=directory)
            return 0

        loaded_count = 0
        for plugin_file in dir_path.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            if await self.load_plugin(str(plugin_file)):
                loaded_count += 1

        logger.info("Plugins loaded from directory", directory=directory, count=loaded_count)
        return loaded_count

    def list_loaded_plugins(self) -> List[str]:
        """List loaded plugin paths."""
        return list(self._loaded_plugins.keys())


class PluginValidator:
    """Validate plugins before loading."""

    @staticmethod
    def validate_plugin(plugin_path: str) -> tuple[bool, List[str]]:
        """Validate plugin file."""
        errors = []
        
        try:
            path = Path(plugin_path)
            if not path.exists():
                errors.append("Plugin file does not exist")
                return False, errors

            # Try to load and validate
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if spec is None or spec.loader is None:
                errors.append("Failed to load plugin spec")
                return False, errors

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check for required functions
            if not hasattr(module, "create_extension"):
                errors.append("Missing create_extension function")
            
            if hasattr(module, "create_extension"):
                try:
                    extension = module.create_extension()
                    if not isinstance(extension, Extension):
                        errors.append("create_extension must return an Extension instance")
                except Exception as e:
                    errors.append(f"create_extension failed: {str(e)}")

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return len(errors) == 0, errors


class PluginPermissions:
    """Manage plugin permissions."""

    REQUIRED_PERMISSIONS = {
        "read_tasks": "Read user tasks",
        "write_tasks": "Create and modify tasks",
        "read_memory": "Read user memory",
        "write_memory": "Create and modify memory",
        "read_notifications": "Read user notifications",
        "write_notifications": "Create and modify notifications",
        "webhook": "Receive webhook events",
    }

    @staticmethod
    def validate_permissions(extension_config: ExtensionConfig) -> tuple[bool, List[str]]:
        """Validate extension permissions."""
        invalid_permissions = []
        
        for perm in extension_config.permissions:
            if perm not in PluginPermissions.REQUIRED_PERMISSIONS:
                invalid_permissions.append(perm)
        
        return len(invalid_permissions) == 0, invalid_permissions

    @staticmethod
    def get_permission_description(permission: str) -> Optional[str]:
        """Get description for a permission."""
        return PluginPermissions.REQUIRED_PERMISSIONS.get(permission)
