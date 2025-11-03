import random
import time


def run_task(task):
    execution_time = random.randint(0,10)
    print(f"Running task {task.id} for {execution_time}")
    time.sleep(execution_time)
