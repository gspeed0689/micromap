from typing import List, Dict
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from sqlalchemy import create_engine, select

from .exceptions import KeyViolationException

from .ormmodels import ORMCategory, ORMFamily, ORMGenus, ORMSpecies, ORMItem, ORMStudy, ORMSample, ORMSlide, Base
from .models import ItemBase, CategoryBase, FamilyBase, GenusBase, SpeciesBase, Study, SampleCreateDTO, SlideCreateDTO

class PostgresqlDataRepository:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:sa@localhost/pollen", echo=True)


    def create_database(self):
        Base.metadata.create_all(self.engine)

    def get_categories(self) -> List[ORMCategory]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMCategory)).all()


    def get_families(self, category_id: str) -> List[ORMFamily]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMFamily).where(ORMFamily.category_id == category_id).order_by(ORMFamily.name)).all()


    def get_genera(self, family_id: str) -> List[ORMGenus]:
        with Session(self.engine) as session:
            if family_id:
                return session.scalars(select(ORMGenus).where(ORMGenus.family_id == family_id).order_by(ORMGenus.name)).all()
            else:
                return session.scalars(select(ORMGenus).order_by(ORMGenus.name)).all()


    def get_species(self, genus_id: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id == genus_id).order_by(ORMSpecies.name)).all()


    def get_studies(self, category_id: str) -> List[ORMStudy]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMStudy).where(ORMStudy.category_id == category_id)).all()

    def add_study(self, new_study: Study):
        try:
            db_item = ORMStudy(
                id = new_study.id,
                description = new_study.description,
                location = new_study.location,
                remarks = new_study.remarks,
                category_id = new_study.category_id)

            with Session(self.engine) as session:
                session.add(db_item)
                session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise KeyViolationException('IntegrityError', str(e.orig))

        return




    def get_samples(self, study_id: str) -> List[ORMSample]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSample).where(ORMSample.study_id == study_id)).all()

    def add_sample(self, new_sample: SampleCreateDTO):
        try:
            db_item = ORMSample(
                id = new_sample.id,
                description = new_sample.description,
                location = new_sample.location,
                age = new_sample.age,
                remarks = new_sample.remarks,
                study_id = new_sample.study_id)

            with Session(self.engine) as session:
                session.add(db_item)
                session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise KeyViolationException('IntegrityError', str(e.orig))

        return

    def get_slides(self, sample_id: str) -> List[ORMSlide]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSlide).where(ORMSlide.sample_id == sample_id)).all()

    def add_slide(self, new_slide: SlideCreateDTO):
        try:
            db_item = ORMSlide(
                id = new_slide.id,
                description = new_slide.description,
                location = new_slide.location,
                sample_id = new_slide.sample_id)

            with Session(self.engine) as session:
                session.add(db_item)
                session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise KeyViolationException('IntegrityError', str(e.orig))

        return

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
        db_item = ORMItem(
            id = new_uuid,
            key_image = new_item.key_image,
            species_id = new_item.species_id,
            genus_id = new_item.genus_id,
            family_id = new_item.family_id,
            study_description = new_item.study_description,
            study_remarks = new_item.study_remarks,
            study_location = new_item.study_location,
            sample_description = new_item.sample_description,
            sample_remarks = new_item.sample_remarks,
            sample_location = new_item.sample_location,
            sample_age = new_item.sample_age,
            slide_description = new_item.slide_description,
            slide_remarks = new_item.slide_remarks,
            )

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def get_items(self, genus_id: UUID = None, family_id: UUID = None) -> List[ORMItem]:
        if genus_id:
            with Session(self.engine) as session:
                return session.scalars(select(ORMItem).where(ORMItem.genus_id == genus_id)).all()
        else:
            with Session(self.engine) as session:
                subq = ( select(ORMGenus.id).where(ORMGenus.family_id == family_id).scalar_subquery() )
                return session.scalars(select(ORMItem).where(or_(ORMItem.genus_id.in_(subq), ORMItem.family_id == family_id))).all()
