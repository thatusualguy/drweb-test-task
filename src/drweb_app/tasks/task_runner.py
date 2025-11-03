import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import select

from src.drweb_app.config import MAX_WORKERS
from src.drweb_app.db.database import AsyncSessionLocal
from src.drweb_app.db.models import Task
from src.drweb_app.tasks.task import run_task


async def _get_next_task() -> Optional[Task]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task).where(Task.start_time == None).order_by(Task.create_time)
        )
        return result.scalars().first()


class TaskRunner:
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self._running = False
        self._semaphore: asyncio.Semaphore | None = None
        self._poll_interval = 0.1
        self._main_task: asyncio.Task | None = None

    async def start(self):
        if self._running:
            return
        self._running = True
        self._semaphore = asyncio.Semaphore(self.max_workers)
        self._main_task = asyncio.create_task(self._run_executor())

    async def stop(self):
        if not self._running:
            return
        self._running = False

        if self._main_task:
            await self._main_task
            self._main_task = None

        if self._semaphore:
            for _ in range(self.max_workers):
                await self._semaphore.acquire()
            for _ in range(self.max_workers):
                self._semaphore.release()

    async def _run_executor(self):
        assert self._semaphore is not None
        while self._running:
            await asyncio.sleep(self._poll_interval)

            task = await _get_next_task()
            if not task:
                continue

            if self._semaphore.locked():
                continue

            await self._semaphore.acquire()
            asyncio.create_task(self._execute_task(task.id))

    async def _execute_task(self, task_id: int):
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Task).where(Task.id == task_id))
                task = result.scalars().first()
                if not task:
                    return

                task.start_time = datetime.now()
                await db.commit()
                await db.refresh(task)

                await run_task(task)

                exec_time = datetime.now() - task.start_time
                task.exec_time = exec_time
                await db.commit()
        finally:
            if self._semaphore:
                self._semaphore.release()


task_runner = TaskRunner(max_workers=MAX_WORKERS)
