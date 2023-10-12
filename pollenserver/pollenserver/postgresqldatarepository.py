from typing import List, Dict
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select

from .ormmodels import ORMCategory, ORMFamily, ORMGenus, ORMSpecies, ORMItem
from .models import ItemBase, CategoryBase, FamilyBase

class PostgresqlDataRepository:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:sa@localhost/pollen", echo=True)


    def create_database(self):
        Base.metadata.create_all(engine)


    def get_families(self) -> List[ORMFamily]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMFamily)).all()


    def get_genera(self, familyid: str) -> List[ORMGenus]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMGenus).where(ORMGenus.family_id == familyid)).all()


    def get_species(self, genusid: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id == genusid)).all()


    def add_category(self, new_category: CategoryBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMCategory(id = new_uuid, name = new_category.name)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid


    def add_family(self, new_family: FamilyBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMFamily(id = new_uuid, name = new_family.name, category_id = new_family.category_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def add_genus(self, new_genus: GenusBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMGenus(id = new_uuid, name = new_genus.name, family_id = new_genus.family_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def add_species(self, new_species: SpeciesBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMSpecies(id = new_uuid, name = new_species.name, genus_id = new_species.genus_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def add_item(self, new_item: ItemBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMItem(id = new_uuid, key_image = new_item.key_image, species_id = new_item.species_id, genus_id = new_item.genus_id, family_id = new_item.family_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid
