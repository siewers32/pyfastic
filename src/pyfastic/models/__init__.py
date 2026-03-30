# src/pyfastic/models/__init__.py

# Exporteer SQLModel zodat je het overal centraal hebt
from sqlmodel import SQLModel

# Importeer al je modellen
# from .imageloralink import ImageLoraLink
from .imageloralink import ImageLoraLink
from .image import Image
from .lora import Lora

# Optioneel: Maak een lijst van wat je exporteert (voor 'from models import *')
__all__ = ["SQLModel", "Image", "Lora", "ImageLoraLink"]