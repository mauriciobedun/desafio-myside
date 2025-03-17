# core/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Criando engine assíncrono para PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)

# Criando sessão assíncrona
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    """Função assíncrona para injetar a sessão do BD em endpoints do FastAPI."""
    async with SessionLocal() as session:
        yield session

