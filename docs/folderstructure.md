Eigen code in een `src` map te zetten, dan scheid je de applicatielogica duidelijk van de configuratiebestanden (`pyproject.toml`, `uv.lock`, `Dockerfile`) die in de root (`/app`) van de container staan.

Geoptimaliseerde Dockerfile voor de `src`-layout:

```dockerfile
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
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Uitleg

* **`PYTHONPATH="/app"`**: Omgevingsvariabele toegevoegd. Dit zorgt ervoor dat Python de `src` map altijd als een module kan vinden, ongeacht vanuit welke map je een script aanroept.
* **`COPY src/ /app/src/`**: De lokale `src` map wordt nu naar `/app/src/` in de container gekopieerd.
* **Uvicorn commando**: De aanroep is nu `src.main:app`. Dit gaat ervan uit dat het bestand `src/main.py` heet en de FastAPI-instantie `app` heet.

### De mappenstructuur ziet er nu zo uit:

```text
mijn-fastapi-app/
├── src/
│   ├── __init__.py
│   └── main.py
├── .venv/
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

### Belangrijke tip voor `pyproject.toml`
Als je `uv` gebruikt met een `src` layout, is het handig om in je `pyproject.toml` aan te geven dat je project in de "non-editable" modus geïnstalleerd kan worden. Controleer of je dit hebt (of voeg het toe):

```toml
[tool.uv]
package = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

http://googleusercontent.com/interactive_content_block/0