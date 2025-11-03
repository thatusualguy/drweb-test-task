from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.drweb_app.config import RESET_UNFINISHED, SERVER_HOST, SERVER_PORT
from src.drweb_app.db.database import get_db, init_db, reset_unfinished_tasks
from src.drweb_app.db.models import Task
from src.drweb_app.schema import TaskId, TaskResponse, StatusEnum
from src.drweb_app.tasks.task_runner import task_runner


@asynccontextmanager
async def lifespan(app: FastAPI):
    docs_url = f"http://{SERVER_HOST}:{SERVER_PORT}/docs"
    print(f"docs at {docs_url}")

    await init_db()

    if RESET_UNFINISHED:
        await reset_unfinished_tasks()

    await task_runner.start()
    yield
    await task_runner.stop()


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello Dr.Web"}


@app.post("/task/new", )
async def new_task(db: AsyncSession = Depends(get_db), ) -> TaskId:
    task = Task(create_time=datetime.now(), )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskId(id=task.id)


@app.get("/task/{task_id}", )
async def say_hello(task_id: int,
                    db: AsyncSession = Depends(get_db),
                    ) -> TaskResponse:
    result = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = result.scalars().first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    if not task.start_time:
        status = StatusEnum.in_queue
    elif not task.exec_time:
        status = StatusEnum.run
    else:
        status = StatusEnum.completed

    return TaskResponse(
        status=status,
        create_time=task.create_time,
        start_time=task.start_time,
        time_to_execute=task.exec_time
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
