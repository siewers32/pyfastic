# Stage 1: Build stage
FROM python:3.12-slim-bookworm AS builder

# Installeer uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Omgevingsvariabelen voor uv (efficiëntie & snelheid)
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# 1. Installeer dependencies (gecached zolang lockfile niet wijzigt)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# 2. Kopieer de broncode (deze staat lokaal in de 'src' map)
COPY src/ /app/src/
COPY pyproject.toml uv.lock /app/

# 3. Project installeren (inclusief de src als package indien gedefinieerd)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Stage 2: Runtime stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Kopieer alleen de virtuele omgeving en de broncode
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Voeg venv toe aan PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Veiligheid: niet als root draaien
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Start FastAPI (let op: we verwijzen nu naar src.main)
# Gebruik de FastAPI CLI direct in productie
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]