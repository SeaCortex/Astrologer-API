FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Lib di sistema necessarie:
# - libsqlite3-0 per sqlite (richiesto da pyswisseph/kerykeion)
# - build-essential per compilare eventuali wheel (pyswisseph)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installa uv (multi-stage "nascosto" da ghcr)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia file di dipendenze
COPY pyproject.toml uv.lock ./

# Installa le dipendenze (in .venv)
RUN uv sync --frozen --no-dev

# Copia il codice dell'app
COPY . .

# La porta esposta è solo informativa
EXPOSE 5000

# Su Railway la porta vera è $PORT, quindi la usiamo se esiste
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-5000}"]

