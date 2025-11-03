import os

MAX_WORKERS = os.getenv('MAX_WORKERS', 2)
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///./app.sqlite")

RESET_UNFINISHED = os.getenv('RESET_UNFINISHED', True)