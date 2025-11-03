import asyncio
import random
from datetime import datetime


async def run_task(task):
    # Имитация задачи, при запуске пишет в stdout
    execution_time = random.randint(0, 10)
    print(f"{datetime.now()} Running task {task.id} for {execution_time}")
    await asyncio.sleep(execution_time)
