from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import DateTime, Integer, Interval
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, )
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False, )
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, )
    exec_time: Mapped[Optional[timedelta]] = mapped_column(Interval, nullable=True, )
