from typing import List, Dict
import uuid
import random

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select

from .ormmodels import ORMFamily, ORMGenus, ORMSpecies

class PostgresqlDataRepository:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:sa@localhost/pollen", echo=True)


    def get_families(self) -> List[ORMFamily]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMFamily)).all()


    def get_genera(self, familyid: str) -> List[ORMGenus]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMGenus).where(ORMGenus.family_id == familyid)).all()


    def get_species(self, genusid: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id == genusid)).all()
