"""Base repository class."""

from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with CRUD operations."""

    def __init__(self, model: type[ModelType]):
        """Initialize repository with model."""
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> ModelType | None:
        """Get single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create new record."""
        obj_dict = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
        db_obj = self.model(**obj_dict)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update existing record."""
        obj_dict = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        for field, value in obj_dict.items():
            setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: str) -> ModelType | None:
        """Delete record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.execute(delete(self.model).where(self.model.id == id))
            await db.commit()
        return obj
