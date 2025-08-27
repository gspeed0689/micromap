from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Float, Boolean
from uuid import UUID
from typing import List

class Base(DeclarativeBase):
    pass


class ORMCatalog(Base):
    __tablename__ = "catalog"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    # Name of the catalog
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class ORMFamily(Base):
    __tablename__ = "family"

    # id of the family
    id: Mapped[UUID] = mapped_column(primary_key=True)

    # Name of the family
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Reference to the Catalog that this Family belongs to
    catalog_id: Mapped[UUID] = mapped_column(ForeignKey("catalog.id"), nullable=False)

    # List of genera that are in this family
    genera: Mapped[List["ORMGenus"]] = relationship(back_populates="family")

    def __repr__(self) -> str:
      return f"Family(id={self.id!r}, name={self.name!r}) genera {self.genera[0].name}"


class ORMGenus(Base):
    __tablename__ = "genus"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=False)
    family: Mapped["ORMFamily"] = relationship(back_populates="genera")
    species: Mapped[List["ORMSpecies"]]= relationship(back_populates="genus")
    is_type: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ORMSpecies(Base):
    __tablename__ = "species"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"))
    genus: Mapped["ORMGenus"] = relationship(back_populates="species")
    subspecies: Mapped[List["ORMSubSpecies"]]= relationship(back_populates="species")
    is_type: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ORMSubSpecies(Base):
    __tablename__ = "subspecies"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"))
    species: Mapped["ORMSpecies"] = relationship(back_populates="subspecies")



class ORMStudy(Base):
    __tablename__ = "study"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)
    is_reference: Mapped[Boolean] = mapped_column(Boolean, nullable=False)


    # Reference to the Catalog that this Study belongs to
    catalog_id: Mapped[UUID] = mapped_column(ForeignKey("catalog.id"), nullable=False)


class ORMSample(Base):
    __tablename__ = "sample"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    study_id: Mapped[UUID] = mapped_column(ForeignKey("study.id"), nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)

    study: Mapped[ORMStudy] = relationship("ORMStudy", lazy='subquery')


class ORMSlide(Base):
    __tablename__ = "slide"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sample_id: Mapped[UUID] = mapped_column(ForeignKey("sample.id"), nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(String, nullable=True)

    sample: Mapped[ORMSample] = relationship("ORMSample", lazy='subquery')


class ORMItem(Base):
    __tablename__ = "item"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    key_image: Mapped[str] = mapped_column(String, nullable=True)
    subspecies_id: Mapped[UUID] = mapped_column(ForeignKey("subspecies.id"), nullable=True)
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"), nullable=True)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"), nullable=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=True)

    comment: Mapped[str] = mapped_column(String, nullable=True)

    slide_id: Mapped[UUID] = mapped_column(ForeignKey("slide.id"), nullable=True)

    slide: Mapped["ORMSlide"] = relationship("ORMSlide", lazy='subquery')

    voxel_width: Mapped[float] = mapped_column(Float, nullable=False)

