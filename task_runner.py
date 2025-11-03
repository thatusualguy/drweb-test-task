import threading
import time
from datetime import datetime

from config import MAX_WORKERS
from database import SessionLocal
from models import Task
from task import run_task


def _get_next_task() -> Task:
    with SessionLocal() as db:
        task = db.query(Task).filter(
            Task.start_time == None
        ).order_by(Task.create_time).first()

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
                    task = _get_next_task()
                    if task:
                        self.running_tasks += 1
                        worker_thread = threading.Thread(
                            target=self._execute_task,
                            args=(task.id,),
                        )
                        worker_thread.start()

            time.sleep(0.1)

    def _execute_task(self, task_id: int):
        try:
            with SessionLocal() as db:
                task = db.query(Task).filter(Task.id == task_id).first()

                task.start_time = datetime.now()
                db.commit()
                db.refresh(task)

                run_task(task)

                exec_time = datetime.now() - task.start_time
                task.exec_time = exec_time
                db.commit()
        finally:
            with self.lock:
                self.running_tasks -= 1


task_runner = TaskRunner(max_workers=MAX_WORKERS)
