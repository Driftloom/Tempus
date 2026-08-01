"""Authentication service for user management and credential validation."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from structlog import get_logger

from app.database.models.user import User
from app.security.auth import PasswordManager

logger = get_logger(__name__)
password_manager = PasswordManager()


class AuthService:
    """Service for authentication operations."""

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> User | None:
        """Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def verify_credentials(
        self,
        db: AsyncSession,
        email: str,
        password: str
    ) -> User | None:
        """Verify user credentials.
        
        Args:
            db: Database session
            email: User email address
            password: Plain text password
            
        Returns:
            User object if credentials are valid, None otherwise
        """
        user = await self.get_user_by_email(db, email)
        
        if not user:
            logger.warning("Authentication failed: user not found", email=email)
            return None
        
        if not user.password_hash:
            logger.warning("Authentication failed: user has no password (OAuth user)", email=email)
            return None
        
        if not password_manager.verify_password(password, user.password_hash):
            logger.warning("Authentication failed: invalid password", email=email)
            return None
        
        logger.info("Authentication successful", user_id=user.id, email=email)
        return user

    async def create_user(
        self,
        db: AsyncSession,
        email: str,
        password: str | None = None,
        display_name: str | None = None
    ) -> User:
        """Create a new user.
        
        Args:
            db: Database session
            email: User email address
            password: Plain text password (optional for OAuth users)
            display_name: Display name
            
        Returns:
            Created User object
        """
        import uuid
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=password_manager.hash_password(password) if password else None,
            display_name=display_name or email.split("@")[0]
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info("User created", user_id=user.id, email=email)
        return user

    async def update_password(
        self,
        db: AsyncSession,
        user_id: str,
        new_password: str
    ) -> User | None:
        """Update user password.
        
        Args:
            db: Database session
            user_id: User ID
            new_password: New plain text password
            
        Returns:
            Updated User object if found, None otherwise
        """
        user = await self.get_user_by_id(db, user_id)
        
        if not user:
            logger.warning("Password update failed: user not found", user_id=user_id)
            return None
        
        user.password_hash = password_manager.hash_password(new_password)
        await db.commit()
        await db.refresh(user)
        
        logger.info("Password updated", user_id=user_id)
        return user
