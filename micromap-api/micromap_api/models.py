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
    family_id: UUID

class Genus(GenusBase):
    id: UUID

    class Config:
        from_attributes = True


class SpeciesBase(BaseModel):
    name: str
    genus_id: UUID

class Species(SpeciesBase):
    id: UUID

    class Config:
        from_attributes = True

class SubSpeciesBase(BaseModel):
    name: str
    species_id: UUID

class SubSpecies(SpeciesBase):
    id: UUID

    class Config:
        from_attributes = True

class StudyBase(BaseModel):
    description: Optional[str]
    location: Optional[str]
    remarks: Optional[str]
    category_id: UUID

class Study(StudyBase):
    id: UUID

    class Config:
        from_attributes = True

class SampleBase(BaseModel):
    description: Optional[str]
    location: Optional[str]
    age: Optional[str]
    remarks: Optional[str]
    study: StudyBase

class SampleCreateDTO(BaseModel):
    id: UUID
    description: Optional[str]
    location: Optional[str]
    age: Optional[str]
    remarks: Optional[str]
    study_id: UUID

class Sample(SampleBase):
    id: UUID

    class Config:
        from_attributes = True

# Slides

class SlideBase(BaseModel):
    description: Optional[str]
    remarks: Optional[str]
    sample: SampleBase

class Slide(SlideBase):
    id: UUID

    class Config:
        from_attributes = True

class SlideCreateDTO(BaseModel):
    id: UUID
    description: Optional[str]
    remarks: Optional[str]
    sample_id: UUID

# -------------

class ItemBase(BaseModel):
    key_image: str
    family_id: Optional[UUID] = None
    genus_id: Optional[UUID] = None
    species_id: Optional[UUID] = None
    subspecies_id: Optional[UUID] = None
    comment: Optional[str] = None

    slide: Slide = None

    voxel_width: float = None

class ItemCreateDTO(BaseModel):
    key_image: str
    family_id: Optional[UUID] = None
    genus_id: Optional[UUID] = None
    species_id: Optional[UUID] = None
    subspecies_id: Optional[UUID] = None
    comment: Optional[str] = None

    slide_id: UUID

    voxel_width: float = None

class Item(ItemBase):
    id: UUID

    class Config:
        from_attributes = True