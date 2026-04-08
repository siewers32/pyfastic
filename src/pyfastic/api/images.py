from typing import Annotated
from celery import result
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pyfastic.tasks import generate_ai_image_task
from pyfastic.dependencies import templates
from sqlalchemy.ext.asyncio import AsyncSession
from pyfastic.database import async_session_maker, get_db
from pyfastic.api.crud import *
from pyfastic.config import settings
from pyfastic.utilities.app_secrets import generate_unique_name
from celery.result import AsyncResult
from datetime import datetime
import os


# Maak de router aan
router = APIRouter(
    prefix="/images",
    tags=["images"]
)

def generate_image_path() -> str:
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    if not os.path.exists(f"{settings.STORAGE_DIR}/{year}/{month}"):
        os.makedirs(f"{settings.STORAGE_DIR}/{year}/{month}")
    return f"{year}/{month}/{generate_unique_name()}.png"

def create_thumbnail_path(image_url: str) -> str:
    if not image_url:
        return None
    return image_url.replace(".png", "_thumb.png")

def convert_str_to_list_floats(input_str: str) -> list:
    # Verwijder spaties en splits op komma
    try:
        return [float(item.strip()) for item in input_str.split(",") if item.strip()]
    except Exception as e:
        print(f"Error converting string to list: {e}")
        return []

def convert_str_to_list_ints(input_str: str) -> list:
    # Verwijder spaties en splits op komma
    try:
        return [int(item.strip()) for item in input_str.split(",") if item.strip()]
    except Exception as e:
        print(f"Error converting string to list: {e}")
        return []

@router.get("/", response_class=HTMLResponse)
async def list_images(request: Request, response_class=HTMLResponse):
    try:
        async with async_session_maker() as session:
            statement = (
                select(Image)
                .options(
                    selectinload(Image.lora_links).selectinload(ImageLoraLink.lora)
                )
            )
            
            result = await session.execute(statement)
            # Gebruik unique() bij joins/relationships om dubbele hoofd-objecten te voorkomen
            images = result.scalars().unique().all()
    except Exception as e:
        print("Database connection failed:", e)
    
    try:
        loras = await get_all_loras(session)
    except Exception as e:
        print("Failed to fetch LoRAs:", e)
        loras = []

    # await session.close()

    return templates.TemplateResponse(
        request=request,
        name="images/index.html",
        context={
            "loras": loras,
            "images": images,
            "thumbnail_urls": {image.id: create_thumbnail_path(image.image_url) for image in images},
            "storage_url": settings.STORAGE_URL
        }
    )

    
@router.post("/add", response_class=HTMLResponse)
async def add_image(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    prompt: str = Form(...),
    negative_prompt: str = Form(...),
    steps: int = Form(...),
    seed:  int = Form(...),    
    width:  int = Form(...),
    height:  int = Form(...),
    lora_ids: str = Form(...),
    scales: str = Form(...)
):
    new_image = await create_image(
        db, 
        name=name, 
        prompt=prompt, 
        negative_prompt=negative_prompt, 
        steps=steps, 
        seed=seed, 
        width=width, 
        height=height,
        image_url=generate_image_path()
    )
  
    lora_ids = convert_str_to_list_ints(lora_ids)
    scale_values = convert_str_to_list_floats(scales)
    
    # loras = await get_loras_by_ids(db, lora_ids=lora_ids)
    for index, lora_id in enumerate(lora_ids):
        lora = await get_lora_by_id(db, lora_id=lora_id)
        # print(f"DEBUG: Linking image {new_image.id} with lora {lora.id} at scale {scale_values[index]} met index {index}")
        db.add(ImageLoraLink(image_id=new_image.id, lora_id=lora.id, scale=scale_values[index]))
    await db.commit()

    task = generate_ai_image_task.delay(
        new_image.id, 
    )

    return templates.TemplateResponse(
        request=request,
        name="images/_status_check.html",
        context={
            "request": request, 
            "task_id": task.id, 
            "prompt": "Generatie gestart..."
        }
    )

@router.post("/delete/{image_id}")
async def delete_image_route(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    # 1. Haal de image data op uit de database
    image = await db.get(Image, image_id)
    
    if not image:
        return RedirectResponse(url="/images", status_code=status.HTTP_303_SEE_OTHER)

    # 2. Verwijder de fysieke bestanden (image + thumbnail)
    # We gebruiken settings.STORAGE_DIR om het volledige pad te bepalen
    full_image_path = os.path.join(settings.STORAGE_DIR, image.image_url)
    thumb_path = create_thumbnail_path(full_image_path)

    try:
        if os.path.exists(full_image_path):
            os.remove(full_image_path)
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception as e:
        print(f"Error bij verwijderen bestand: {e}")
        # We gaan door met de DB verwijdering, zelfs als het bestand al weg was

    # 3. Verwijder uit de database
    # De links (ImageLoraLink) worden meestal automatisch verwijderd als je 
    # cascade="all, delete-orphan" in je SQLAlchemy model hebt staan.
    await db.delete(image)
    await db.commit()

    # 4. Redirect terug naar het overzicht
    return RedirectResponse(url="/images", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/status/{task_id}", response_class=HTMLResponse)
async def get_task_status(
    request: Request, 
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verbind met de Celery task via de ID
 
    result = AsyncResult(task_id)

     
    # 2. Check de status van de task
    if result.state == "SUCCESS": 
        task_output = result.result    
        db_id = task_output["id"]  # Pas dit aan op basis van wat je task precies teruggeeft
            
        # Haal de afbeelding op uit de DB om de URL/data te krijgen
        db_image = await db.get(Image, db_id)
        
        if not db_image:
            return "<p class='error'>Afbeelding niet gevonden in database.</p>"

        image_thumbnail_url = create_thumbnail_path(db_image.image_url)

        # Return het 'klaar' fragment (de afbeelding zelf)
        return templates.TemplateResponse(
            request=request,
            name="images/_image_card.html",
            context={
                "request": request, 
                "image": db_image,
                "thumbnail_url": image_thumbnail_url
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
            name="images/_status_check.html",
            context={
                "request": request, 
                "task_id": task_id, 
                "prompt": "De AI is nog bezig..." 
            }
        )
    