from xml.parsers.expat import model

from time import time
from pathlib import Path
from PIL import Image as PILImage # Voor thumbnails
from pyfastic.config import settings
from pyfastic.models import Image
from datetime import datetime
import os

class ImageService:
    def __init__(self):
        self.storage_path = Path(settings.STORAGE_DIR)
        self.storage_path.mkdir(parents=True, exist_ok=True)
         
    def generate_image(self, img: Image) -> None:
        model = self.get_model(img)
        image = model.generate_image(
            seed=img.seed,
            width=img.width,
            height=img.height,
            num_inference_steps=img.steps,
            guidance=0.0,
            image_strength=None,
            scheduler=None,
            prompt=img.prompt,
            negative_prompt=img.negative_prompt,
        )
        image.save(f"{self.storage_path}/{img.image_url}")

    def get_model(self, img: Image) :
        from mflux.models.common.config import ModelConfig
        from mflux.models.z_image import ZImageTurbo
        return ZImageTurbo(
            model_config=ModelConfig.z_image_turbo(),
            model_path=settings.AI_MODEL,
            quantize=None,
            lora_paths=[f"{settings.LORA_PATH}/{link.lora.name}" for link in img.lora_links],
            lora_scales=[link.scale for link in img.lora_links]
        )
    
    def create_thumbnail(self, original_path: str):
        """Logica voor het maken van een kleine versie."""
        # Gebruik Pillow om te resizen
        pass

# Instantieer de service zodat je hem elders kunt importeren
image_service = ImageService()  # Je zou hier een Image object kunnen injecteren als dat nodig is


