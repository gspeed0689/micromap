import os
from typing import List
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from sqlalchemy import create_engine, select

from .exceptions import KeyViolationException, EntityDoesNotExistException

from .ormmodels import ORMCategory, ORMFamily, ORMGenus, ORMSpecies, ORMItem, ORMStudy, ORMSample, ORMSlide, Base
from .models import ItemBase, CategoryBase, Category, FamilyBase, Family, GenusBase, Genus, SpeciesBase, Species, Study, SampleCreateDTO, SlideCreateDTO


class PostgresqlDataRepository:
    def __init__(self):
        server = os.getenv("PGHOSTADDR", os.getenv("PGHOST", "localhost"))
        database = os.getenv("PGDATABASE", "micromap")
        user = os.getenv("PGUSER", "postgres")
        password = os.getenv("PGPASSWORD", "postgres")
        port = os.getenv("PGPORT", "5432")
        self.engine = create_engine(f"postgresql://{user}:{password}@{server}:{port}/{database}", echo=True)

    def create_database(self):
        Base.metadata.create_all(self.engine)

    # Categories

    def get_categories(self) -> List[ORMCategory]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMCategory)).all()

    def add_category(self, new_category: CategoryBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMCategory(id = new_uuid, name = new_category.name)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_category(self, updated_category: Category):
        with Session(self.engine) as session:
            try:
                category = session.scalars(select(ORMCategory).where(ORMCategory.id == updated_category.id)).one()
                category.name = updated_category.name
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    # Families

    def get_families(self, category_id: str) -> List[ORMFamily]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMFamily).where(ORMFamily.category_id == category_id).order_by(ORMFamily.name)).all()

    def add_family(self, new_family: FamilyBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMFamily(id = new_uuid, name = new_family.name, category_id = new_family.category_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_family(self, updated_family: Family):
        with Session(self.engine) as session:
            try:
                family = session.scalars(select(ORMFamily).where(ORMFamily.id == updated_family.id)).one()
                family.name = updated_family.name
                family.category_id = updated_family.category_id
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    # Genera

    def get_genera(self, family_id: str) -> List[ORMGenus]:
        with Session(self.engine) as session:
            if family_id:
                return session.scalars(select(ORMGenus).where(ORMGenus.family_id == family_id).order_by(ORMGenus.name)).all()
            else:
                return session.scalars(select(ORMGenus).order_by(ORMGenus.name)).all()

    def add_genus(self, new_genus: GenusBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMGenus(id = new_uuid, name = new_genus.name, family_id = new_genus.family_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_genus(self, updated_genus: Genus):
        with Session(self.engine) as session:
            try:
                genus = session.scalars(select(ORMGenus).where(ORMGenus.id == updated_genus.id)).one()
                genus.name = updated_genus.name
                genus.family_id = updated_genus.family_id
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    # Species

    def get_species(self, genus_id: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id == genus_id).order_by(ORMSpecies.name)).all()

    def add_species(self, new_species: SpeciesBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMSpecies(id = new_uuid, name = new_species.name, genus_id = new_species.genus_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_species(self, updated_species: Species):
        with Session(self.engine) as session:
            try:
                species = session.scalars(select(ORMSpecies).where(ORMSpecies.id == updated_species.id)).one()
                species.name = updated_species.name
                species.genus_id = updated_species.genus_id
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    def get_species_for_category(self, category_id: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            all_families = ( select(ORMFamily.id).where(ORMFamily.category_id == category_id).scalar_subquery() )
            all_genera = ( select(ORMGenus.id).where(ORMGenus.family_id.in_(all_families)).scalar_subquery() )
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id.in_(all_genera)).order_by(ORMSpecies.name)).all()

    # Studies

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

    # Samples

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
                remarks = new_slide.remarks,
                sample_id = new_slide.sample_id)

            with Session(self.engine) as session:
                session.add(db_item)
                session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            raise KeyViolationException('IntegrityError', str(e.orig))

        return










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
