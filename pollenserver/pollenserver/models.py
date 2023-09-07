from pydantic import BaseModel
from uuid import UUID

class FamilyBase(BaseModel):
    name: str

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