Top! Nu de basis van je database (Docker) staat, is het tijd om de "tijdmachine" van je database in te richten: **Alembic**. Omdat je `SQLModel` gebruikt, gaan we Alembic zo instellen dat hij automatisch je Python-klassen vergelijkt met de database en de juiste SQL-scripts genereert.

Hier is het stappenplan om dit vanuit je root-directory in te richten:

### Stap 1: De initiële setup
We hebben de map al bepaald, maar voer dit commando uit om de structuur aan te maken als je dat nog niet gedaan had:

```bash
uv run alembic init src/project_naam/migrations
```

### Stap 2: Verbind Alembic met je code (`env.py`)
Dit is de belangrijkste stap. Je moet Alembic vertellen waar je `SQLModel`-definities staan en welke database-URL hij moet gebruiken.

Open `src/project_naam/migrations/env.py` en pas deze regels aan:

```python
# 1. Importeer je SQLModel en je settings
from sqlmodel import SQLModel
from project_naam.config import settings
from project_naam.models import Image  # Importeer AL je modellen hier!

# 2. Koppel de metadata voor 'autogenerate'
target_metadata = SQLModel.metadata

# 3. Zorg dat de database URL uit je .env wordt gehaald
# In .env staat niet de URI. Stel deze samen in config.py 
```
```python
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Stelt de URI samen: postgresql://user:pass@server:port/db"""
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

```
def get_url():
    return settings.SQLALCHEMY_DATABASE_URI

# Pas in de functies 'run_migrations_offline' en 'run_migrations_online' 
# de url aan naar get_url()
```

### Stap 3: Pas `alembic.ini` aan
In de root vind je `alembic.ini`. Zorg dat het pad naar je migraties klopt:

```ini
script_location = src/project_naam/migrations
# Je kunt sqlalchemy.url hier leeg laten of verwijderen, 
# omdat we dit nu via env.py en je .env regelen.
```

### Stap 4: Je eerste migratie genereren
Nu de verbinding is gelegd, laten we Alembic kijken naar je `Image` model en dit vergelijken met de (nog lege) database in Docker.

```bash
# Genereer het script (autogenerate ziet dat de tabel 'image' nog niet bestaat)
uv run alembic revision --autogenerate -m "Initial migration"
```

Kijk nu in `src/project_naam/migrations/versions/`. Daar staat een nieuw `.py` bestand met de `upgrade` en `downgrade` logica voor je tabellen.

### Stap 5: De migratie uitvoeren
Voer het script uit om de tabellen daadwerkelijk in Postgres aan te maken:

```bash
uv run alembic upgrade head
```

---

### Tips voor je Workflow

* **Nieuwe tabel?** Voeg je model toe in `models.py`, zorg dat het geïmporteerd is in `env.py`, en draai opnieuw `revision --autogenerate`.
* **Docker & Migraties:** In productie wil je dat migraties automatisch draaien. Je kunt je Docker `CMD` aanpassen naar een bash-script dat eerst `alembic upgrade head` doet en dan pas je FastAPI app start.
* **Check de status:** Met `uv run alembic current` zie je op welke versie je database nu zit.

### Samenvattend commando-overzicht:
| Commando | Wat doet het? |
| :--- | :--- |
| `alembic revision --autogenerate -m "bericht"` | Maakt een nieuw migratiescript op basis van je modellen. |
| `alembic upgrade head` | Past de nieuwste wijzigingen toe op je database. |
| `alembic downgrade -1` | Draait de allerlaatste wijziging terug (handig bij fouten). |

Wil je dat ik een opstartscript (`entrypoint.sh`) voor je Dockerfile schrijf dat automatisch de migraties uitvoert voordat de app start?

http://googleusercontent.com/interactive_content_block/0