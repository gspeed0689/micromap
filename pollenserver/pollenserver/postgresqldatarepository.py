from typing import List, Dict
import uuid
import random

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select

from .models import Family, Genus
from .ormmodels import ORMFamily, ORMGenus

class PostgresqlDataRepository:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:sa@localhost/pollen", echo=True)


    def get_families(self) -> Dict[str, Family]:
        result = {}
        with Session(self.engine) as session:
            stmt = select(ORMFamily)
            for fam in session.scalars(stmt):
                result[fam.id] = Family(name=fam.name)

        return result


    def get_genera(self, familyid: str) -> Dict[str, Genus]:
        result = {}
        with Session(self.engine) as session:
            stmt = select(ORMGenus).where(ORMGenus.family_id == familyid)
            for gen in session.scalars(stmt):
                result[gen.id] = Genus(name=gen.name)

        return result

