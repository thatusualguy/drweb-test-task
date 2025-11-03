import os

MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite+aiosqlite:///./app.sqlite")

# Сбрасывать ли незавершённые задачи при старте
RESET_UNFINISHED = os.getenv('RESET_UNFINISHED', 'true').lower() in ('1', 'true', 'yes')

SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))
