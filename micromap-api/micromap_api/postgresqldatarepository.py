import os
from typing import List
from uuid import UUID, uuid4

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_, and_
from sqlalchemy import create_engine, select, func

from .models import ItemCreateDTO

from .exceptions import KeyViolationException, EntityDoesNotExistException

from .ormmodels import ORMCatalog, ORMFamily, ORMGenus, ORMSpecies, ORMItem, ORMStudy, ORMSample, ORMSlide, Base
from .models import CatalogBase, Catalog, FamilyBase, Family, GenusBase, Genus, SpeciesBase, Species, Study, SampleCreateDTO, SlideCreateDTO
import random


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

    # Catalogs

    def get_catalogs(self) -> List[ORMCatalog]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMCatalog)).all()

    def add_catalog(self, new_catalog: CatalogBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMCatalog(id = new_uuid, name = new_catalog.name)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_catalog(self, updated_catalog: Catalog):
        with Session(self.engine) as session:
            try:
                catalog = session.scalars(select(ORMCatalog).where(ORMCatalog.id == updated_catalog.id)).one()
                catalog.name = updated_catalog.name
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    # Families

    def get_families(self, catalog_id: str) -> List[ORMFamily]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMFamily).where(ORMFamily.catalog_id == catalog_id).order_by(ORMFamily.name)).all()

    def add_family(self, new_family: FamilyBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMFamily(id = new_uuid, name = new_family.name, catalog_id = new_family.catalog_id)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def update_family(self, updated_family: Family):
        with Session(self.engine) as session:
            try:
                family = session.scalars(select(ORMFamily).where(ORMFamily.id == updated_family.id)).one()
                family.name = updated_family.name
                family.catalog_id = updated_family.catalog_id
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    def get_genera(self, family_id: str, is_include_if_genus_is_type = True) -> List[ORMGenus]:
        '''This fucntion is used to fill in the genera drop down menu using the family_id
        #Additionally if the is_include_if_genus_is_type is untick then it wont return is_type
        Reference filtering handles by hiding the option is not clicked'''
        if is_include_if_genus_is_type == True:
            with Session(self.engine) as session:
                # Fetch all genera for the given family
                genera = session.scalars(
                    select(ORMGenus).where(ORMGenus.family_id == family_id).order_by(ORMGenus.name)
                ).all()
                return [
                {
                    "id": str(genus.id),  # Ensure ID is a string for JSON compatibility
                    "name": genus.name
                }
                for genus in genera
            ]
        else: # if we dont want is_type genus
            with (Session(self.engine) as session):
                # Fetch all genera for the given family
                genera = session.scalars(
                    select(ORMGenus).where(ORMGenus.family_id == family_id)
                    .where(ORMGenus.is_type != True)  # Filter to exclude is_type = True
                    .order_by(ORMGenus.name)
                ).all()
                return [
                    {
                        "id": str(genus.id),  # Ensure ID is a string for JSON compatibility
                        "name": genus.name
                    }
                    for genus in genera
                ]


    def add_genus(self, new_genus: GenusBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMGenus(id = new_uuid,
                           name = new_genus.name,
                           family_id = new_genus.family_id,
                           is_type = new_genus.is_type)

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
                genus.is_type = updated_genus.is_type
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    # Species

    def get_species(self, genus_id: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id == genus_id).order_by(ORMSpecies.name)).all()

    def add_species(self, new_species: SpeciesBase)-> UUID:
        new_uuid = uuid4()
        db_item = ORMSpecies(id = new_uuid,
                             name = new_species.name,
                             genus_id = new_species.genus_id,
                             is_type=new_species.is_type)

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
                species.is_type = updated_species.is_type
                session.commit()
            except sqlalchemy.exc.NoResultFound:
                raise EntityDoesNotExistException()

    def get_species_for_catalog(self, catalog_id: str) -> List[ORMSpecies]:
        with Session(self.engine) as session:
            all_families = ( select(ORMFamily.id).where(ORMFamily.catalog_id == catalog_id).scalar_subquery() )
            all_genera = ( select(ORMGenus.id).where(ORMGenus.family_id.in_(all_families)).scalar_subquery() )
            return session.scalars(select(ORMSpecies).where(ORMSpecies.genus_id.in_(all_genera)).order_by(ORMSpecies.name)).all()

    # Studies

    def get_studies(self, catalog_id: str) -> List[ORMStudy]:
        with Session(self.engine) as session:
            return session.scalars(select(ORMStudy).where(ORMStudy.catalog_id == catalog_id)).all()

    def add_study(self, new_study: Study):
        try:
            db_item = ORMStudy(
                id = new_study.id,
                description = new_study.description,
                location = new_study.location,
                remarks = new_study.remarks,
                is_reference = new_study.is_reference,
                catalog_id = new_study.catalog_id)

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

    def add_item(self, new_item: ItemCreateDTO)-> UUID:
        new_uuid = uuid4()
        db_item = ORMItem(
            id = new_uuid,
            key_image = new_item.key_image,
            family_id = new_item.family_id,
            genus_id = new_item.genus_id,
            species_id = new_item.species_id,
            subspecies_id = new_item.subspecies_id,
            comment = new_item.comment,
            slide_id = new_item.slide_id,
            voxel_width = new_item.voxel_width)

        with Session(self.engine) as session:
            session.add(db_item)
            session.commit()

        return new_uuid

    def get_items(self,
                  species_id = None,
                  genus_id: UUID = None,
                  max_results = None,
                  reference_only: bool = False,
                  family_id: UUID = None,
                  offset=0,
                  include_genus_type = True,
                  include_species_type = True) -> List[ORMItem]:

        # this function works by input. If family is selected, the family is retuned, so all genera and related species are returned
        # if genera is selected, genus and related species are returned
        # if species is selcted only species is returned.

        # the item table only has either family_id, genus_id or species_id cannot be both.

        # is_type is a flag that pretains to if a there is a limit on the depth of precision on certain genera/species
        # is_type only concern non-reference material
        # Sometimes users may want to filter out is_type #ToDO: highlight if Is_type on the website
        # is_type does not filter from family drop down. It only filters out if is_reference in the study field.

        # TODO: there should be are more elegant way to build this query...
        items_ids = []
        #add a condition, if: include non-reference, then reference and non-reference returned. If exclude is_type. Then only on the non-reference filter out is_type true.
        if not reference_only: #this can be fitered by type
            with Session(self.engine) as session:
                if species_id:
                    if include_species_type == True:
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .where(ORMItem.species_id == species_id)
                        ).all()
                    else: #only select where not is is_type
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .join(ORMSpecies, ORMItem.species_id == ORMSpecies.id)
                            .where(
                                ORMItem.species_id == species_id,
                                ORMSpecies.is_type != True #not is_type
                            )
                        ).all()
                elif genus_id: #genus first check to inlcude non-reference
                    if include_genus_type == True: #condition if by default returning genus_is_type, include items that are under the  species
                        subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id == genus_id).scalar_subquery()
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .where(or_(ORMItem.genus_id == genus_id, ORMItem.species_id.in_(subq_species)))
                        ).all()
                    else: #the same fetch request but exclude Is_type
                        subq_species = select(ORMSpecies.id).where(ORMSpecies.genus_id == genus_id).scalar_subquery()
                        #dont select is_type false
                        items_ids = session.scalars(
                            select(ORMItem.id)
                            .join(ORMGenus,
                                  ORMGenus.id == ORMItem.genus_id)  # Ensure we join with ORMGenus to check is_type
                            .where(
                                or_(
                                    # Case 1: Item belongs to the genus, and genus is not a reference type (is_type != True)
                                    and_(
                                        ORMItem.genus_id == genus_id,  # Genus ID matches
                                        ORMGenus.is_type != True  # Genus is not of type (non-reference)
                                    ),
                                    # Case 2: Item belongs to a species of the genus
                                    ORMItem.species_id.in_(subq_species)  # Item belongs to a species under the genus
                                )
                            )
                        ).all()

                elif family_id:
                    # 2 subqueries are required to capture alll those that are genera and species under this item
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
                        .where(ORMStudy.is_reference == True)
                        .where(or_(ORMItem.family_id == family_id, ORMItem.genus_id.in_(subq_genera), ORMItem.species_id.in_(subq_species)))
                    ).all()


        if items_ids:
            #Use a limit before the heavy query
            paginated_ids = items_ids[offset: offset + max_results]# this ensure that the output is limited to a max number

        #return items not just ids (more efficent)
            with Session(self.engine) as session:
                items = session.scalars(
                select(ORMItem).where(ORMItem.id.in_(paginated_ids))
                 ).all()

            # Shuffle after query but with a seed so it is reproducible
            random.seed(0)
            random.shuffle(items)  # This shuffles the actual ORMItem objects

            return items
        return [] # return an empty list if nothing else


    def get_genera_by_letter(self, letter: str, is_include_if_genus_is_type: bool = True):
        """
        Fetch all genera whose names start with the given letter, including family ID and name,
        ordered alphabetically.

        If `is_include_if_genus_is_type` is False, genera where ORMGenus.is_type is True will be excluded.
        """
        with Session(self.engine) as session:
            query = (
                select(
                    ORMGenus.id,
                    ORMGenus.name,
                    ORMFamily.id,
                    ORMFamily.name
                )
                .join(ORMFamily, ORMGenus.family_id == ORMFamily.id)
                .where(ORMGenus.name.ilike(f'{letter}%'))
            )

            if not is_include_if_genus_is_type:
                query = query.where(ORMGenus.is_type == False)

            query = query.order_by(ORMGenus.name)

            genera = session.execute(query).all()

        genera_dicts = [{
            'genus_id': genus_id,
            'genus_name': genus_name,
            'family_id': family_id,
            'family_name': family_name
        } for genus_id, genus_name, family_id, family_name in genera]

        return genera_dicts

        #if genera include genrea-TYPE not selected then dont include genera_type

        # Convert list of tuples to list of dictionaries
        genera_dicts = [{
            'genus_id': genus_id,
            'genus_name': genus_name,
            'family_id': family_id,
            'family_name': family_name
        } for genus_id, genus_name, family_id, family_name in genera]

        return genera_dicts

##### for the dashboard summary: Part 1 is a test to show species count######
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
