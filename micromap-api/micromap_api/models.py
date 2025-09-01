from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class MicromapBaseModel(BaseModel):
    id: Optional[UUID]  # IDs are not nullable in the ORM model, but can either be set or generated in this API.

    class Config:
        from_attributes = True


class Catalog(MicromapBaseModel):
    name: str


class Family(MicromapBaseModel):
    name: str
    catalog_id: UUID


class Genus(MicromapBaseModel):
    name: str
    family_id: UUID
    is_type: bool = False


class Species(MicromapBaseModel):
    name: str
    genus_id: UUID
    is_type: bool = False


class SubSpecies(MicromapBaseModel):
    name: str
    species_id: UUID


class Study(MicromapBaseModel):
    description: Optional[str]
    location: Optional[str]
    remarks: Optional[str]
    catalog_id: UUID
    is_reference: bool = False


class Sample(MicromapBaseModel):
    description: Optional[str]
    location: Optional[str]
    age: Optional[str]
    remarks: Optional[str]
    study: Study

class SampleCreateDTO(MicromapBaseModel):  # Contains study_id instead of Study
    description: Optional[str]
    location: Optional[str]
    age: Optional[str]
    remarks: Optional[str]
    study_id: UUID


class Slide(MicromapBaseModel):
    description: Optional[str]
    remarks: Optional[str]
    sample: Sample

class SlideCreateDTO(MicromapBaseModel):  # Contains sample_id instead of Sample
    description: Optional[str]
    remarks: Optional[str]
    sample_id: UUID


class Item(MicromapBaseModel):
    key_image: str
    family_id: Optional[UUID] = None
    genus_id: Optional[UUID] = None
    species_id: Optional[UUID] = None
    subspecies_id: Optional[UUID] = None
    comment: Optional[str] = None
    slide: Slide = None
    voxel_width: float = None

class ItemCreateDTO(MicromapBaseModel):  # Contains slide_id instead of Slide
    key_image: str
    family_id: Optional[UUID] = None
    genus_id: Optional[UUID] = None
    species_id: Optional[UUID] = None
    subspecies_id: Optional[UUID] = None
    comment: Optional[str] = None
    slide_id: UUID
    voxel_width: float = None
