from datetime import datetime, timezone
from sqlmodel import DateTime, Field, Relationship, SQLModel
from typing import List, Optional
from enum import Enum
from pyfastic.models.imageloralink import ImageLoraLink

    
class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ImageBase(SQLModel):
    name: str
    prompt: str
    image_url: Optional[str] = None
    seed: int | None = 1
    steps: int | None = 9
    width: int | None = 512
    height: int | None = 512
    negative_prompt: Optional[str] = None
    status: str = Field(default=Status.PENDING)

class Image(ImageBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # loras: List["Lora"] = Relationship(back_populates="images", link_model=ImageLoraLink)
    lora_links: List[ImageLoraLink] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan", # <--- Voor SQLAlchemy logica
        },
        back_populates="image",
    )
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True), 
        sa_column_kwargs={"server_default": "now()"},
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": "now()",
            "onupdate": lambda: datetime.now(timezone.utc) # Python-side refresh
        },
        default_factory=lambda: datetime.now(timezone.utc)
    )
    
class ImageGenerate(ImageBase):
    lora_ids: List[int] = []
    scales: List[float] = []
