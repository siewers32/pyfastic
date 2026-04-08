import asyncio
from datetime import datetime
import os
from requests import session
from pyfastic.celery_app import celery_app
from pyfastic.database import async_session_maker 
from pyfastic.models import Image, ImageLoraLink
from pyfastic.config import settings
from pyfastic.services.translation_service import translator
from pyfastic.services.image_gererator import image_service
from sqlmodel import select
from sqlalchemy.orm import selectinload


# def create_image_name(image_id: int, created_at: datetime) -> str:
#     month = created_at.strftime("%m")
#     year = created_at.strftime("%Y")
#     if not os.path.exists(f"{settings.STORAGE_DIR}/{year}/{month}"):
#         os.makedirs(f"{settings.STORAGE_DIR}/{year}/{month}")
#     return f"{settings.STORAGE_DIR}/{year}/{month}/{image_id}.png"


@celery_app.task(name="generate_ai_image", bind=True)
def generate_ai_image_task(self, image_id: int):
    # Gebruik run_until_complete voor de async logica binnen Celery
    return asyncio.get_event_loop().run_until_complete(
        _async_task_logic(image_id)
    )

async def _async_task_logic(image_id: int):
    # Dankzij de nieuwe database.py hoeven we hier geen ingewikkelde configs te doen
    async with async_session_maker() as session:
        # We laden de ketting volledig in: Image -> lora_links -> lora
        statement = (
            select(Image)
            .where(Image.id == image_id)
            .options(
                selectinload(Image.lora_links)  # Laad de pivot-records
                .selectinload(ImageLoraLink.lora)  # Laad de Lora-details PER pivot-record
            )
        )
        
        result = await session.execute(statement)
        db_image = result.scalar_one_or_none()

        if not db_image:
            return "Niet gevonden"
            
    try:
        await asyncio.to_thread(image_service.generate_image, db_image)
        await asyncio.to_thread(image_service.create_thumbnail, f"{settings.STORAGE_DIR}/{db_image.image_url}") 
        
        # Simulatie van succesvolle afronding
        db_image.status = "completed"
        
    except Exception as e:
        db_image.status = "failed"
        print(f"Error tijdens generatie: {e}")
        # Eventueel: raise self.retry(exc=e) als je Celery retries wilt gebruiken
        
    finally:
        # 4. Finaliseer de status in de database
        await session.commit()
        
    # We kunnen db_image.status veilig teruggeven omdat het object niet 'expired' is
    return {"id": image_id, "status": db_image.status}


@celery_app.task(name="generate_translation", bind=True)
def generate_translation_task(self, text_id: int):
    # Gebruik run_until_complete voor de async logica binnen Celery
    return asyncio.get_event_loop().run_until_complete(
        _async_translate_logic(text_id)
    )

async def _async_translate_logic(prompt: str):
    try:
        final_output = await asyncio.to_thread(translator.translate_prompt, prompt)

    except Exception as e:
        print(f"Error tijdens translator generatie: {e}")
        # Eventueel: raise self.retry(exc=e) als je Celery retries wilt gebruiken
    return { 
        "status": "Translation completed",
        "translation": final_output
    }
 