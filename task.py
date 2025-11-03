import random
import time
from datetime import datetime


def run_task(task):
    execution_time = random.randint(0,10)
    print(f"{datetime.now()} Running task {task.id} for {execution_time}")
    time.sleep(execution_time)
