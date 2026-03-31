import sys
from os.path import abspath, dirname, join
from sqlalchemy import text

src_path = abspath(join(dirname(__file__), '.', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# print("DEBUG: Current sys.path:", sys.path)

from pyfastic.database import engine, async_session_maker
from pyfastic.models import Image, Lora, ImageLoraLink
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload # Belangrijk voor performance
import asyncio

async def get_db_connection():
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
            
            for img in images:
                print(f"\nAfbeelding: {img.name} (ID: {img.id})")
                print(f"Prompt: {img.prompt}")
                
                if not img.lora_links:
                    print("  - Geen LoRA's gekoppeld.")
                
                for link in img.lora_links:
                    # Hier heb je toegang tot info uit ALLE DRIE de tabellen:
                    # 1. img (Image tabel)
                    # 2. link.scale (Link tabel)
                    # 3. link.lora.name (Lora tabel)
                    print(f"  - LoRA: {link.lora.name} | Scale in link: {link.scale} | Trigger: {link.lora.trigger}")

    except Exception as e:
        print("Database connection failed:", e)
            
    #         test = text(
    #             "SELECT * FROM image \
    #             JOIN imageloralink ill ON image.id = ill.image_id \
    #             JOIN lora ON ill.lora_id = lora.id;"
    #         )
    #         print("Database connection successful:")
    #         result = await session.execute(test)
    #         rows = result.fetchall()
    #         for row in rows:
    #             print(row.id)
    # except Exception as e:
    #     print("Database connection failed:", e)


if __name__ == "__main__":
    asyncio.run(get_db_connection())
