from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DATABASE_URL
from models import Base, Task

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_unfinished_tasks():
    with Session(engine) as db:
        unfinished_tasks = db.query(Task).filter(Task.start_time.is_not(None), Task.exec_time.is_(None)).all()
        for unfinished_task in unfinished_tasks:
            unfinished_task.start_time = None
        db.commit()
