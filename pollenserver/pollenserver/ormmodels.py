from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from uuid import UUID
from typing import List

class Base(DeclarativeBase):
    pass


class ORMCategory(Base):
    __tablename__ = "category"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    # Name of the category
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class ORMFamily(Base):
    __tablename__ = "family"

    # id of the family
    id: Mapped[UUID] = mapped_column(primary_key=True)

    # Name of the family
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Reference to the Category that this Family belongs to
    category_id: Mapped[UUID] = mapped_column(ForeignKey("category.id"), nullable=False)

    # List of genera that are in this family
    genera: Mapped[List["ORMGenus"]] = relationship(back_populates="family")

    def __repr__(self) -> str:
      return f"Family(id={self.id!r}, name={self.name!r}) genera {self.genera[0].name}"


class ORMGenus(Base):
    __tablename__ = "genus"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=False)
    family: Mapped["ORMFamily"] = relationship(back_populates="genera")
    species: Mapped[List["ORMSpecies"]]= relationship(back_populates="genus")


class ORMSpecies(Base):
    __tablename__ = "species"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"))
    genus: Mapped["ORMGenus"] = relationship(back_populates="species")


class ORMItem(Base):
    __tablename__ = "item"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    key_image: Mapped[str] = mapped_column(String, nullable=True)
    species_id: Mapped[UUID] = mapped_column(ForeignKey("species.id"), nullable=True)
    genus_id: Mapped[UUID] = mapped_column(ForeignKey("genus.id"), nullable=True)
    family_id: Mapped[UUID] = mapped_column(ForeignKey("family.id"), nullable=True)

