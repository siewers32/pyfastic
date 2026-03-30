import asyncio
from pyfastic.celery_app import celery_app
from pyfastic.database import async_session_maker 
from pyfastic.models import Image, ImageLoraLink
from pyfastic.config import settings
from pyfastic.services.image_gererator import image_service
from sqlmodel import select
from sqlalchemy.orm import selectinload

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

        # Simulatie van succesvolle afronding
        db_image.status = "completed"
        db_image.image_url = f"{settings.STORAGE_DIR}/{db_image.id}.png"
        
    except Exception as e:
        db_image.status = "failed"
        print(f"Error tijdens generatie: {e}")
        # Eventueel: raise self.retry(exc=e) als je Celery retries wilt gebruiken
        
    finally:
        # 4. Finaliseer de status in de database
        await session.commit()
        
    # We kunnen db_image.status veilig teruggeven omdat het object niet 'expired' is
    return {"id": image_id, "status": db_image.status}