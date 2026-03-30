from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, DateTime
from typing import List
from pyfastic.models.imageloralink import ImageLoraLink

 
class Lora(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # image_model: int
    name: str
    scale: float
    trigger: str | None = None
    # images: List["Image"] = Relationship(back_populates="loras", link_model=ImageLoraLink)
    image_links: List[ImageLoraLink] = Relationship(
        back_populates="lora",
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
