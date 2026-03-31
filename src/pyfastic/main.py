from fastapi import FastAPI, Request
from pyfastic.utilities.app_secrets import generate_keys_json
from pyfastic.config import settings
from pyfastic.api import images, loras, translations  # Importeer je router bestand
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pyfastic.dependencies import templates

app = FastAPI(title=settings.PROJECT_NAME)

# ... onder je app = FastAPI() ...
app.include_router(images.router)
app.include_router(loras.router)
app.include_router(translations.router)

# templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")


@app.get("/", response_class=HTMLResponse)
async def root_read(request: Request):
    
    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
        context={"request": request, "message": "Welkom op de homepage van je AI applicatie."}
    )

@app.get("/secrets")
async def read_secrets():
    value = generate_keys_json()
    return {"message": "Secrets generated!", "keys": value}

