from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

class ImageLoraLink(SQLModel, table=True):
    image_id: int | None = Field(default=None, foreign_key="image.id", primary_key=True, ondelete="CASCADE")
    lora_id: int | None = Field(default=None, foreign_key="lora.id", primary_key=True, ondelete="CASCADE")
    scale: float | None = Field(default=1.0)

    image: "Image" = Relationship(back_populates="lora_links")
    lora: "Lora" = Relationship(back_populates="image_links")