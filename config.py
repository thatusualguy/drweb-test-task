import os

MAX_WORKERS = os.getenv('MAX_WORKERS', 2)
DATABASE_URL = os.getenv('DATABASE_URL', "sqlite:///./app.sqlite")
DROP_DB_ON_START = os.getenv('DROP_DB_ON_RESTART', False)