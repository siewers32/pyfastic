from typing import Annotated
from celery import result
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pyfastic.tasks import generate_ai_image_task, generate_translation_task
from pyfastic.dependencies import templates
from sqlalchemy.ext.asyncio import AsyncSession
from pyfastic.database import get_db
from pyfastic.api.crud import *
from celery.result import AsyncResult

# Maak de router aan
router = APIRouter(
    prefix="/translations",
    tags=["translations"]
)

@router.get("/", response_class=HTMLResponse)
async def show_translation_form(request: Request):
    
    return templates.TemplateResponse(
        request=request,
        name="translations/index.html",
    )

@router.post("/translate", response_class=HTMLResponse)
async def do_translation(
    request: Request, 
    db: AsyncSession = Depends(get_db),
    prompt: str = Form(...)
):
    task = generate_translation_task.delay(prompt)
    print(f"Translation task ID: {task.id}")
    return templates.TemplateResponse(
        request=request,
        name="translations/_status_check.html",
        context={
            "request": request,
            "task_id": task.id,
            "prompt": "Generatie gestart..."
        }
    )


@router.get("/status/{task_id}", response_class=HTMLResponse)
async def get_task_status(
    request: Request, 
    task_id: str,
):
    # 1. Verbind met de Celery task via de ID
 
    result = AsyncResult(task_id)

     
    # 2. Check de status van de task
    if result.state == "SUCCESS": 
        task_output = result.result    
        status = task_output["status"]  # Pas dit aan op basis van wat je task precies teruggeeft
        translation = task_output["translation"]
            
        # Return het 'klaar' fragment (de afbeelding zelf)
        return templates.TemplateResponse(
            request=request,
            name="translations/_translation_result.html",
            context={
                "request": request,
                "translation": translation,
                "status": status
            }
        )


    elif result.state == "FAILURE":
        # Er ging iets mis in de worker (bijv. MLX crash)
        return f"<div class='error'>Generatie mislukt: {result.info}</div>"

    else:
        # Status is PENDING of STARTED: we laten de loader staan.
        # Door dit fragment terug te sturen met dezelfde hx-get, blijft HTMX pollen.
        return templates.TemplateResponse(
            request=request,
            name="translations/_status_check.html",
            context={
                "request": request, 
                "task_id": task_id, 
                "prompt": "De AI is nog bezig..." 
            }
        )
    