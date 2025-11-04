FROM ghcr.io/astral-sh/uv:debian-slim
LABEL authors="thatusualguy"

WORKDIR /app

# Install uv
#COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY src ./src

# Expose the port FastAPI will run on
EXPOSE 8000

# Run app
ENTRYPOINT ["uv", "run", "uvicorn", "src.drweb_app.main:app", "--host", "0.0.0.0", "--port", "8000"]