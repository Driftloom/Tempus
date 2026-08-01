"""User repository."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, dict, dict]):
    """Repository for User model."""

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
