from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Task
from schema import TaskId, TaskResponse, StatusEnum
from task_runner import task_runner


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task_runner.start()
    yield
    task_runner.stop()


app = FastAPI(
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello Dr.Web"}


@app.post("/task/new", )
async def new_task(db: Session = Depends(get_db), ) -> TaskId:
    task = Task(create_time=datetime.now(), )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskId(id=task.id)


@app.get("/task/{task_id}", )
async def say_hello(task_id: int,
                    db: Session = Depends(get_db),
                    ) -> TaskResponse:
    task: Task | None = db.query(Task).filter(Task.id == task_id).first()

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
