from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import RESET_UNFINISHED
from database import get_db, init_db, reset_unfinished_tasks
from models import Task
from schema import TaskId, TaskResponse, StatusEnum
from task_runner import task_runner


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    if RESET_UNFINISHED:
        await reset_unfinished_tasks()

    task_runner.start()
    yield
    task_runner.stop()


print("docs at http://localhost:8000/docs")

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
