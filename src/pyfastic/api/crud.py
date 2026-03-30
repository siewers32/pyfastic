
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from pyfastic.models import Image, Lora, ImageLoraLink
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_all_images(db: AsyncSession):
    statement = select(Image)
    results = await db.execute(statement)
    return results.scalars().all()

async def get_imageloralinks(db: AsyncSession):
    statement = select(Image, ImageLoraLink, Lora).join(
        ImageLoraLink, Image.id == ImageLoraLink.image_id
    ).join(
        Lora, ImageLoraLink.lora_id == Lora.id  
    )

    results = await db.execute(statement)
    rows = results.all()
        
    output = []
    for image, imageloralink, lora in rows:
        # We bouwen een simpele dict. 
        output.append({
            "image_name": image.name,
            "image_prompt": image.prompt,
            "lora_name": lora.name,
            "scale": imageloralink.scale, # De extra kolom
            "image_id": image.id
        })
    return output


async def get_image_by_id(db: AsyncSession, image_id: int):
    statement = select(Image).where(Image.id == image_id)
    results = await db.execute(statement)
    return results.scalars().first()

async def get_lora_by_id(db: AsyncSession, lora_id: int):
    statement = select(Lora).where(Lora.id == lora_id)
    results = await db.execute(statement)
    return results.scalars().first()

async def get_all_loras(db: AsyncSession):
    statement = select(Lora)
    results = await db.execute(statement)
    return results.scalars().all()

async def get_loras_by_ids(db: AsyncSession, lora_ids: list[int]):
    statement = select(Lora).where(Lora.id.in_(lora_ids))
    results = await db.execute(statement)
    return results.scalars().all()

async def get_imageloralinks_by_image_id(db: AsyncSession, image_id: int):
    statement = select(ImageLoraLink).where(ImageLoraLink.image_id == image_id)
    results = await db.execute(statement)
    return results.scalars().all()

async def create_lora(db: AsyncSession, name: str, scale: float, trigger: str | None = None):
    try:
         new_lora = Lora(name=name, scale=scale, trigger=trigger)
         db.add(new_lora)
         await db.commit()
         await db.refresh(new_lora)
         return new_lora
    except IntegrityError:
            await db.rollback() # Maak de foutieve actie ongedaan
            raise ValueError("Lora bestaat niet of data is incompleet.")
    except Exception as e:
            await db.rollback() # Maak de foutieve actie ongedaan
            raise e

async def create_image(
          db: AsyncSession, 
          name: str, 
          prompt: str, 
          negative_prompt: str = "", 
          steps: int = 9, 
          width: int = 512, 
          height: int = 512, 
          seed: int = 1
        ):
    try:
        new_image = Image(
            name=name,
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            width=width,
            height=height,
            seed=seed
        )
        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)
        return new_image
    except IntegrityError:
        await db.rollback() # Maak de foutieve actie ongedaan
        raise ValueError("Image bestaat niet of data is incompleet.")
    except Exception as e:
        await db.rollback() # Maak de foutieve actie ongedaan
        raise e

async def create_image_lora_link(db: AsyncSession, image_id: int, lora_id: int, scale: float = 1.0):
    try:
        from pyfastic.models.imageloralink import ImageLoraLink
        new_link = ImageLoraLink(image_id=image_id, lora_id=lora_id, scale=scale) 
        db.add(new_link)
        await db.commit()
        await db.refresh(new_link)
        return new_link
    except IntegrityError:
        await db.rollback() # Maak de foutieve actie ongedaan
        raise ValueError("Link bestaat niet of data is incompleet.")
    except Exception as e:
        await db.rollback() # Maak de foutieve actie ongedaan
        raise e 