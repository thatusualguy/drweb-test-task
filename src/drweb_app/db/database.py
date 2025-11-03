from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.drweb_app.config import DATABASE_URL
from src.drweb_app.db.models import Base, Task

engine = create_async_engine(DATABASE_URL, )

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def reset_unfinished_tasks():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.start_time.is_not(None), Task.exec_time.is_(None))
        )
        unfinished_tasks = result.all()
        for unfinished_task in unfinished_tasks:
            unfinished_task.start_time = None
        await session.commit()
