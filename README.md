# Base Fastapi app with UV

### Installation
* [Install using uv](https://docs.astral.sh/uv/guides/integration/fastapi/)
* `uv init --lib`
* `uv add fastapi --extra standard`
* `uv add hatchling`
* Create `main.py`
* Run in development mode `uv run fastapi dev src/pyfastic/main.py`
* Run in production mode `uv run fastapi run src/pyfastic/main.py`
* In productie via Dockerfile wordt dit:
    * `CMD ["fastapi", "run", "src/main.py", "--port", "8000"]`

### Run Postgres
* In `docker-compose.yml` zijn twee services gedefieerd.
    * db - De postgres server
    * adminer - postgres webclient
* start database en client met `docker compose up -d`

### Alembic
* `uv run alembic revision --autogenerate -m "comment"`
* `uv run alembic upgrade head`

### Run Celery en Redis
* Start de containers met `docker compose up -d`
* Check of Redis en Celery draaien: `docker compose run --rm worker uv run pip freeze | grep celery`
* Opstarten met `PYTHONPATH=src uv run python -m celery -A pyfastic.celery_app worker --loglevel=info --pool=solo`
