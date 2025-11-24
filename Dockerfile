FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
# libsqlite3-0 is required by pyswisseph/kerykeion
# build-essential provides gcc for compiling pyswisseph
RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose the port
EXPOSE 5000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
