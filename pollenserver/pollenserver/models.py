from typing import Optional
from pydantic import BaseModel
from uuid import UUID

class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    id: UUID

    class Config:
        from_attributes = True


class FamilyBase(BaseModel):
    name: str
    category_id: UUID

class Family(FamilyBase):
    id: UUID

    class Config:
        from_attributes = True


class GenusBase(BaseModel):
    name: str

class Genus(GenusBase):
    id: UUID

    class Config:
        from_attributes = True


class SpeciesBase(BaseModel):
    name: str

class Species(GenusBase):
    id: UUID

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    key_image: str
    family_id: Optional[UUID] = None
    genus_id: Optional[UUID] = None
    species_id: Optional[UUID] = None

class Item(ItemBase):
    id: UUID

    class Config:
        from_attributes = True