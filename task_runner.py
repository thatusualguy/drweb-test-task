import threading
import time
from datetime import datetime

from config import MAX_WORKERS
from database import AsyncSessionLocal
from models import Task
from task import run_task
from sqlalchemy import select
import asyncio


async def _get_next_task() -> Task | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task).where(Task.start_time == None).order_by(Task.create_time)
        )
        task = result.scalars().first()
        return task


class TaskRunner:
    def __init__(self, max_workers=2):
        self.max_workers = max_workers
        self.running_tasks = 0
        self.lock = threading.Lock()
        self.executor_thread = None
        self.running = False

    def start(self):
        self.running = True
        self.executor_thread = threading.Thread(target=self._run_executor)
        self.executor_thread.start()

    def stop(self):
        self.running = False
        if self.executor_thread:
            self.executor_thread.join()

    def _run_executor(self):
        while self.running:
            with self.lock:
                if self.running_tasks < self.max_workers:
                    task = asyncio.run(_get_next_task())
                    if task:
                        self.running_tasks += 1
                        worker_thread = threading.Thread(
                            target=self._execute_task,
                            args=(task.id,),
                        )
                        worker_thread.start()

            time.sleep(0.1)

    def _execute_task(self, task_id: int):
        async def _do_work():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Task).where(Task.id == task_id))
                task = result.scalars().first()
                if not task:
                    return

                task.start_time = datetime.now()
                await db.commit()
                await db.refresh(task)

                # run_task is sync and blocking by design; run it in a thread-aware way
                run_task(task)

                exec_time = datetime.now() - task.start_time
                task.exec_time = exec_time
                await db.commit()

        try:
            asyncio.run(_do_work())
        finally:
            with self.lock:
                self.running_tasks -= 1


task_runner = TaskRunner(max_workers=MAX_WORKERS)
