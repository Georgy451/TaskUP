from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Строка подключения теперь совпадает с alembic.ini
DATABASE_URL = "postgresql+asyncpg://home:georgdobriy222222@localhost:5432/FastAPI"
print(f"[DEBUG] DATABASE_URL used for connection: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session
