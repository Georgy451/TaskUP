from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Явно указываем IPv4 localhost
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres"
print(f"[DEBUG] DATABASE_URL used for connection: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session
