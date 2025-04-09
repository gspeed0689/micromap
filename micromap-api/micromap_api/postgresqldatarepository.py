import os
from typing import List, Dict
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import select, or_
from sqlalchemy import create_engine, select, func


from .models import settings #used to get max_results as defined in .env

from .exceptions import KeyViolationException, EntityDoesNotExistException

from .ormmodels import ORMCategory, ORMFamily, ORMGenus, ORMSpecies, ORMItem, ORMStudy, ORMSample, ORMSlide, Base
from .models import ItemBase, CategoryBase, Category, FamilyBase, Family, GenusBase, Genus, SpeciesBase, Species, Study, SampleCreateDTO, SlideCreateDTO
import random # to randomise family and genus queries


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


    #modify existing get ge_genera to return a result with a flag on result if species is undefined
    def get_genera(self, family_id: str) -> List[ORMGenus]:
        with Session(self.engine) as session:
            # Fetch all genera for the given family
            genera = session.scalars(
                select(ORMGenus).where(ORMGenus.family_id == family_id).order_by(ORMGenus.name)
            ).all()

            #Perhaps this part may not be needed
            #Find genera that have items without a species
            undefined_species_genus_ids = session.scalars(
                select(ORMGenus.id)
                .join(ORMItem, ORMGenus.id == ORMItem.genus_id)
                .where(ORMItem.species_id.is_(None))  # Correct NULL check
                .group_by(ORMGenus.id)
            ).all()

            # Return a list of dictionaries with an extra field
            return [
                {
                    "id": str(genus.id),  # Ensure ID is a string for JSON compatibility
                    "name": genus.name,
                    "has_undefined_species": genus.id in undefined_species_genus_ids
                }
                for genus in genera
            ]

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
#this function works by input. If family is slected, genus, family and species is retuned
#if genera is selected,  family and genus are returned
#if species is selcted only species is returned.

#subqueries are used to accomadate the database structure.
    def get_items(self,
                  species_id = None,
                  genus_id: UUID = None,
                  user_max_results = None,
                  include_non_reference: bool = True,
                  family_id: UUID = None,
                  offset=0,
                  is_include_if_genus_is_type = True) -> List[ORMItem]:

        items_ids = []
        #add a condition, if: include non-reference, then reference and non-reference returned. If exclude is_type. Then only on the non-reference filter out is_type true.
        if include_non_reference == True:
            with Session(self.engine) as session:
                if species_id:
                    items_ids = session.scalars(
                        select(ORMItem.id)
                        .where(ORMItem.species_id == species_id)
                    ).all()
                elif genus_id: #genus inlcude non-reference
                    if is_include_if_genus_is_type ==True: #condition if by default returning genus_is_type
                        #EDWIN: WOULD YOU SAY THE DEFULAT IS TRUE? OR IS TEH DEFAULT FALSE? What if it is null?
                        subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id == genus_id).scalar_subquery()
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .where(
                                or_(
                                    ORMItem.genus_id == genus_id,
                                    ORMItem.species_id.in_(subq_species)
                                )
                            )
                        ).all()
                    else: # the same but we dont want to include genus_is_type_items
                        subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id == genus_id).scalar_subquery()
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .where(
                                or_(
                                    ORMItem.genus_id == genus_id,
                                    ORMItem.species_id.in_(subq_species)
                                )
                            )
                        ).where(ORMItem.istype == False).all()

                elif family_id:
                    subq_genera = select(ORMGenus.id).where(ORMGenus.family_id == family_id).scalar_subquery()
                    subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id.in_(subq_genera)).scalar_subquery()
                    items_ids = session.scalars(
                        select(ORMItem.id)
                        .where(or_(ORMItem.family_id == family_id, ORMItem.genus_id.in_(subq_genera), ORMItem.species_id.in_(subq_species)))
                    ).all()
        else:    #exclude all non-reference. in this case is_check does not need to be considered. Filter out the non-reference
            with Session(self.engine) as session:
                if species_id:
                    items_ids = session.scalars(
                        select(ORMItem.id)  # need to join slide to item to study
                        .join(ORMSlide, ORMItem.slide_id == ORMSlide.id)
                        .join(ORMSample, ORMSample.id == ORMSlide.sample_id)
                        .join(ORMStudy, ORMStudy.id == ORMSample.study_id)
                        .where(ORMStudy.is_reference == True)
                        .where(ORMItem.species_id == species_id)
                    ).all()
                elif genus_id:
                    subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id == genus_id).scalar_subquery()
                    items_ids = session.scalars(
                        select(ORMItem.id) #need to join slide to item to study
                        .join(ORMSlide, ORMItem.slide_id == ORMSlide.id)
                        .join(ORMSample, ORMSample.id == ORMSlide.sample_id)
                        .join(ORMStudy, ORMStudy.id == ORMSample.study_id)
                        .where(ORMStudy.is_reference == True)
                        .where(or_(ORMItem.genus_id == genus_id, ORMItem.species_id.in_(subq_species)))
                    ).all()
                elif family_id:
                    subq_genera = select(ORMGenus.id).where(ORMGenus.family_id == family_id).scalar_subquery()
                    subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id.in_(subq_genera)).scalar_subquery()
                    items_ids = session.scalars(
                        select(ORMItem.id)
                        .join(ORMSlide, ORMItem.slide_id == ORMSlide.id)
                        .join(ORMSample, ORMSample.id == ORMSlide.sample_id)
                        .join(ORMStudy, ORMStudy.id == ORMSample.study_id)
                        .where(ORMStudy.is_reference== True)
                        .where(or_(ORMItem.family_id == family_id, ORMItem.genus_id.in_(subq_genera), ORMItem.species_id.in_(subq_species)))
                    ).all()


        if items_ids:
            #Randomize order before returning. seeded so order should be the same
            random.seed(42)
            random.shuffle(items_ids)  # This is better than sorting with random key
            paginated_ids = items_ids[offset: offset + user_max_results]# this ensure that the output is limited to a max number

        #return items not just ids (more efficent)
            with Session(self.engine) as session:
                items = session.scalars(
                select(ORMItem).where(ORMItem.id.in_(paginated_ids))
                 ).all()
            return items
        return [] # return an empty list if nothing else



        """Fetch all genera whose names start with the given letter, along with family ID and name, ordered alphabetically."""

    def get_genera_by_letter(self, letter: str):
        """Fetch all genera whose names start with the given letter, including family ID and name, ordered alphabetically."""
        with Session(self.engine) as session:
            genera = session.execute(
                select(
                    ORMGenus.id,  #
                    ORMGenus.name,
                    ORMFamily.id,  #
                    ORMFamily.name).join(
                    ORMFamily, ORMGenus.family_id == ORMFamily.id
                )
                .where(ORMGenus.name.ilike(f'{letter}%'))
                .order_by(ORMGenus.name)
            ).all()  # Returns a list of tuples

        # Convert list of tuples to list of dictionaries
        # Convert list of tuples to list of dictionaries
        genera_dicts = [{
            'genus_id': genus_id,
            'genus_name': genus_name,
            'family_id': family_id,
            'family_name': family_name
        } for genus_id, genus_name, family_id, family_name in genera]

        return genera_dicts

        # for the dashboard summary: Part 1 is a test to show species count
    #species count
    def get_species_count(self) -> int:  # Add 'self'
        with Session(self.engine) as session:
            return session.scalar(select(func.count()).select_from(ORMSpecies))

    #genera count
    def get_genera_count(self) -> int:  # Add 'self'
        with Session(self.engine) as session:
            return session.scalar(select(func.count()).select_from(ORMGenus))

    #family count
    def get_family_count(self) -> int:  # Add 'self'
        with Session(self.engine) as session:
            return session.scalar(select(func.count()).select_from(ORMFamily))


    #Return a list of family by letter. Used for alphabetical search
    def get_family_by_letter(self, letter: str):
        """Fetch families whose names start with the given letter, along with genus count."""
        with Session(self.engine) as session:
            families = session.scalars(
                select(ORMFamily)
                .where(func.lower(ORMFamily.name).startswith(letter.lower()))  # Case-insensitive filter
                .order_by(ORMFamily.name)
            ).all()

            family_data = []
            for family in families:
                # Count genera linked to this family
                genus_count = session.execute(
                    select(func.count(ORMGenus.id))
                    .where(ORMGenus.family_id == family.id)
                ).scalar_one()  # Get integer result

                # Count items linked either directly to family OR indirectly via genus
                item_count = session.execute(
                    select(func.count(ORMItem.id))
                    .where(
                        (ORMItem.family_id == family.id) |
                        (ORMItem.genus_id.in_(
                            select(ORMGenus.id).where(ORMGenus.family_id == family.id)
                        ))
                    )
                ).scalar_one()

                family_data.append({
                    "id": str(family.id),
                    "name": family.name,
                    "genus_count": genus_count,  # Count of genera in this family
                    "item_count": item_count  # Count of items linked to this family
                })

        return family_data



