from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Boolean, CheckConstraint
from uuid import UUID
from typing import List


class ORMBase(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True)


class ORMCatalog(ORMBase):
    __tablename__ = "catalog"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class ORMFamily(ORMBase):
    __tablename__ = "family"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    catalog_id: Mapped[UUID] = mapped_column(ForeignKey("catalog.id"), nullable=False)
    genera: Mapped[List["ORMGenus"]] = relationship(back_populates="family")  # populates genus.family


class ORMGenus(ORMBase):
    __tablename__ = "genus"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=False)
    family: Mapped[ORMFamily] = relationship(back_populates="genera")  # populates family.genera
    species: Mapped[List["ORMSpecies"]]= relationship(back_populates="genus")  # populates species.genus
    is_type: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ORMSpecies(ORMBase):
    __tablename__ = "species"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"))
    genus: Mapped[ORMGenus] = relationship(back_populates="species")  # populates genus.species
    subspecies: Mapped[List["ORMSubSpecies"]] = relationship(back_populates="species")  # populates subspecies.species
    is_type: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ORMSubSpecies(ORMBase):
    __tablename__ = "subspecies"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"))
    species: Mapped[ORMSpecies] = relationship(back_populates="subspecies")  # populates species.subspecies


class ORMStudy(ORMBase):
    __tablename__ = "study"

    description: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)
    is_reference: Mapped[bool] = mapped_column(Boolean, nullable=False)
    catalog_id: Mapped[UUID] = mapped_column(ForeignKey("catalog.id"), nullable=False)


class ORMSample(ORMBase):
    __tablename__ = "sample"

    study_id: Mapped[UUID] = mapped_column(ForeignKey("study.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)
    study: Mapped[ORMStudy] = relationship(ORMStudy, lazy='subquery')


class ORMSlide(ORMBase):
    __tablename__ = "slide"

    sample_id: Mapped[UUID] = mapped_column(ForeignKey("sample.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)
    sample: Mapped[ORMSample] = relationship(ORMSample, lazy='subquery')


class ORMItem(ORMBase):
    __tablename__ = "item"

    key_image: Mapped[str] = mapped_column(String, nullable=True)
    subspecies_id: Mapped[UUID] = mapped_column(ForeignKey("subspecies.id"), nullable=True)
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"), nullable=True)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"), nullable=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=True)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    slide_id: Mapped[UUID] = mapped_column(ForeignKey("slide.id"), nullable=True)
    slide: Mapped[ORMSlide] = relationship(ORMSlide, lazy='subquery')
    voxel_width: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        # This constraint enforces one and only one of the taxonomic levels should be used.
        CheckConstraint(
            "(subspecies_id IS NOT NULL)::int + "
            "(species_id IS NOT NULL)::int + "
            "(genus_id IS NOT NULL)::int + "
            "(family_id IS NOT NULL)::int = 1",
            name="force_single_taxon",
        ),
    )
