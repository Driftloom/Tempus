"""Dependency injection container."""

from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.memory_repository import MemoryRepository
from app.database.repositories.task_repository import TaskRepository
from app.database.repositories.user_repository import UserRepository
from app.database.session import AsyncSessionLocal
from app.email.service import EmailService
from app.memory.service import MemoryService
from app.notifications.service import NotificationService
from app.router.service import RouterService
from app.tasks.service import TaskService

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        """Initialize container."""
        self._singletons: dict[type, Any] = {}
        self._factories: dict[type, Callable] = {}

    def register_singleton(self, interface: type[T], implementation: T) -> None:
        """Register a singleton dependency."""
        self._singletons[interface] = implementation
        logger.debug("Registered singleton", interface=interface.__name__)

    def register_factory(self, interface: type[T], factory: Callable[..., T]) -> None:
        """Register a factory dependency."""
        self._factories[interface] = factory
        logger.debug("Registered factory", interface=interface.__name__)

    def get(self, interface: type[T]) -> T:
        """Get a dependency from the container."""
        if interface in self._singletons:
            return self._singletons[interface]
        if interface in self._factories:
            return self._factories[interface]()
        raise ValueError(f"Dependency not registered: {interface.__name__}")

    def get_with_session(self, interface: type[T], session: AsyncSession) -> T:
        """Get a dependency with a database session."""
        if interface in self._factories:
            return self._factories[interface](session=session)
        raise ValueError(f"Dependency not registered: {interface.__name__}")


# Global container instance
container = Container()


def register_dependencies() -> None:
    """Register all dependencies in the container."""

    # Register repositories
    container.register_factory(UserRepository, lambda session=None: UserRepository())
    container.register_factory(TaskRepository, lambda session=None: TaskRepository())
    container.register_factory(MemoryRepository, lambda session=None: MemoryRepository())

    # Register services
    container.register_factory(
        TaskService,
        lambda session=None: TaskService(
            task_repo=container.get_with_session(TaskRepository, session) if session else TaskRepository()
        )
    )
    container.register_factory(
        MemoryService,
        lambda session=None: MemoryService(
            memory_repo=container.get_with_session(MemoryRepository, session) if session else MemoryRepository()
        )
    )
    container.register_factory(
        EmailService,
        lambda session=None: EmailService(
            user_repo=container.get_with_session(UserRepository, session) if session else UserRepository()
        )
    )
    container.register_factory(
        NotificationService,
        lambda session=None: NotificationService()
    )
    container.register_factory(
        RouterService,
        lambda session=None: RouterService()
    )

    logger.info("Dependencies registered in container")


@lru_cache
def get_container() -> Container:
    """Get the global container instance (cached)."""
    return container


def get_db_session() -> AsyncSession:
    """Get a database session for dependency injection."""
    return AsyncSessionLocal()


def get_user_repository(session: AsyncSession) -> UserRepository:
    """Get user repository with session."""
    return container.get_with_session(UserRepository, session)


def get_task_repository(session: AsyncSession) -> TaskRepository:
    """Get task repository with session."""
    return container.get_with_session(TaskRepository, session)


def get_memory_repository(session: AsyncSession) -> MemoryRepository:
    """Get memory repository with session."""
    return container.get_with_session(MemoryRepository, session)


def get_task_service(session: AsyncSession) -> TaskService:
    """Get task service with session."""
    return container.get_with_session(TaskService, session)


def get_memory_service(session: AsyncSession) -> MemoryService:
    """Get memory service with session."""
    return container.get_with_session(MemoryService, session)


def get_email_service(session: AsyncSession) -> EmailService:
    """Get email service with session."""
    return container.get_with_session(EmailService, session)


def get_notification_service() -> NotificationService:
    """Get notification service."""
    return container.get(NotificationService)


def get_router_service() -> RouterService:
    """Get router service."""
    return container.get(RouterService)
