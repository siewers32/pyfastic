# Gebruik een specifieke Python 3.12 image van uv
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_LINK_MODE=copy

WORKDIR /app

# Kopieer de lockfile en project file
COPY pyproject.toml uv.lock ./

# Installeer de dependencies precies zoals in de lockfile staat
# De --python vlag dwingt uv om binnen de container 3.12 te gebruiken
RUN uv sync --no-install-project --python 3.12

COPY . .

RUN uv sync --frozen --python 3.12

ENTRYPOINT ["uv", "run"]