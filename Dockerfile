FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:${PATH}"

COPY . .

EXPOSE 8000

# NIENTE variabili qui, solo un intero
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
