import os
from hashlib import sha256
from typing import Optional, List, Sequence

from fastapi import FastAPI, Query, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute, APIRouter
from fastapi.security import APIKeyHeader

from .exceptions import KeyViolationException, EntityDoesNotExistException
from .ormmodels import ORMItem, ORMFamily, ORMGenus, ORMSpecies, ORMStudy, ORMSample, ORMSlide, ORMCatalog
from .postgresqldatarepository import PostgresqlDataRepository
from .models import (CatalogBase, Catalog, FamilyBase, Family, Genus, GenusBase, Species, SpeciesBase, ItemCreateDTO,
                     Item, Study, SampleCreateDTO, Sample, SlideCreateDTO, Slide)


def generate_unique_id(route: APIRoute):
    return f"{route.name}"

async def check_api_key(api_key: str = Security(APIKeyHeader(name='x-api-key', auto_error=False))):
    """
    Checks if the hash of the provided API key matches the one stored in the .env file.
    Raises a 401 error (Unauthorized) if it doesn't match.
    """
    if api_key is None:
        raise HTTPException(status_code=401, detail="Missing API Key")

    if sha256(api_key.encode()).hexdigest() != os.getenv("API_KEY_HASH"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

# Define a public and secure route. The secure route checks the API key with check_api_key.
public = APIRouter()
secure = APIRouter(dependencies=[Depends(check_api_key)])

app = FastAPI(generate_unique_id_function=generate_unique_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(", "),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repository = PostgresqlDataRepository()
repository.create_database()  # Create all tables. Will not attempt to recreate tables already present.


@public.get("/")
async def get_root():
    return {"message": "MicroMap API"}


@public.get("/items/", response_model=List[Item])
async def get_items(
        family_id: Optional[str] = Query(default=None),
        genus_id: Optional[str] = Query(default=None),
        species_id: Optional[str] = Query(default=None),
        include_genus_type: bool = Query(default=True),
        include_species_type: bool = Query(default=True),
        reference_only: bool = Query(default=False),
        study: Optional[str] = Query(default=None),
        sample: Optional[str] = Query(default=None),
        slide: Optional[str] = Query(default=None),
        order: str = os.environ.get('DEFAULT_ORDER', 'abundance'),
        max_results: int = Query(default=100),
        page: int = Query(default=1)
) -> List[ORMItem]:
    """
    Use:
    This function get the items we use to show the thumbnails
    users arguments specified by the user.
    The function is returns according to the highest taxonomic detail specified by the user
        species
        genus
        family

    Offset and typesetting are performed here before the get_items function is called

    Explanation of params:
    Handles a new query for pollen images.

    :param family_id: A specific pollen family.
    :param genus_id: A specific genus of a family.
    :param species_id: A specific species of a genus.
    :param include_genus_type: Include genus types.
    :param include_species_type: Include species types.
    :param reference_only: Only include items from reference studies.
    :param study: A specific study. - TODO: not used yet
    :param sample: A specific sample in a study. - TODO: not used yet
    :param slide: A specific slide in a sample. - TODO: not used yet
    :param order: The order in which the results are returned. - TODO: not used yet
    :param max_results: Maximum number of results returned.
    :param page: The page number of the results.
    :return: A dictionary with matches.
    """
    # Build search query
    max_results = min(int(os.environ.get('MAX_RESULTS', 500)), max_results)  # Clip to MAX_RESULTS

    # Calculate offset
    offset = (page - 1) * max_results

    # Fetch results based on available filters
    if species_id:
        return repository.get_items(
            species_id=species_id,
            include_species_type=include_species_type,
            reference_only=reference_only,
            max_results=max_results,
            offset=offset)
    elif genus_id:
        return repository.get_items(
            genus_id=genus_id,
            include_genus_type=include_genus_type,
            reference_only=reference_only,
            max_results=max_results,
            offset=offset)
    elif family_id:
        return repository.get_items(
            family_id=family_id,
            reference_only=reference_only,
            max_results=max_results,
            offset=offset)
    else:
        # TODO: Search on database level.
        pass

    return []

@secure.post("/items/")
async def post_item(item: ItemCreateDTO):
    return { "id": repository.add_item(item) }


@public.get("/catalogs/", response_model=Sequence[Catalog])
async def get_catalogs() -> Sequence[ORMCatalog]:
    return repository.get_catalogs()

@secure.post("/catalogs/", status_code=201)
async def post_catalog(catalog: CatalogBase):
    return { "id": repository.add_catalog(catalog) }

@secure.put("/catalogs/", status_code=200, responses = {404: {"description": "Catalog does not exist"}})
async def put_catalog(catalog: Catalog):
    try:
        repository.update_catalog(catalog)
    except EntityDoesNotExistException:
        return 404
    return


@public.get("/families/", response_model=Sequence[Family])
async def get_families(catalog_id: str) -> Sequence[ORMFamily]:
    return repository.get_families(catalog_id)

@secure.post("/families/", status_code=201)
async def post_family(family: FamilyBase):
    return { "id": repository.add_family(family) }

@secure.put("/families/", status_code=200, responses = {404: {"description": "Family does not exist"}})
async def put_family(family: Family):
    try:
        repository.update_family(family)
    except EntityDoesNotExistException:
        return 404
    return

@public.get("/families/count/")
async def get_family_count():
    num =  repository.get_family_count()
    return {"count": num}

# #not used
# @public.get("/family/letter/{letter}")
# async def family_by_letter(letter: str):
#     family_list = repository.get_family_by_letter(letter)
#
#     return family_list


@public.get("/genera/", response_model=Sequence[Genus])
async def get_genera(family_id: str, include_genus_type: bool = True) -> Sequence[ORMGenus]:
    """
    Used for alphabetical search and genera drop down additional argument to not include genera_is_type
    """
    return repository.get_genera(family_id, include_genus_type)

# @public.get("/genera_for_alphabetical/")
# def get_genera_for_alphabetical():
#     data = repository.get_all_genera()
#     return data

@secure.post("/genera/", status_code=201)
async def post_genus(genus: GenusBase):
    return { "id": repository.add_genus(genus) }

@secure.put("/genera/", status_code=200, responses = {404: {"description": "Genus does not exist"}})
async def put_genus(genus: Genus):
    try:
        repository.update_genus(genus)
    except EntityDoesNotExistException:
        return 404
    return

@public.get("/genera/letter/{letter}")
async def get_genera_by_letter(letter: str, include_genus_type: bool = True):
    """Return GENERA by capital first letter, for alphabetical search, removes if_genus_is_type"""
    genera_list = repository.get_genera_by_letter(letter, include_genus_type)
    return genera_list

@public.get("/genera/count/")
async def get_genera_count():
    num =  repository.get_genera_count()
    return {"count": num}


@public.get("/species/", response_model=Sequence[Species])
async def get_species(genera_id: Optional[str] = None, catalog_id: Optional[str] = None) -> Sequence[ORMSpecies]:
    """ returns species according to genus_id used in species drop down and alphabetical search"""
    if genera_id:
        return repository.get_species(genera_id)
    if catalog_id:
        return repository.get_species_for_catalog(catalog_id)

@secure.post("/species/", status_code=201)
async def post_species(species: SpeciesBase):
    return { "id": repository.add_species(species) }

@secure.put("/species/", status_code=200, responses = {404: {"description": "Species does not exist"}})
async def put_species(species: Species):
    try:
        repository.update_species(species)
    except EntityDoesNotExistException:
        return 404
    return

@public.get("/species/count/")
async def get_species_count():
    num =  repository.get_species_count()
    return {"count": num}


@public.get("/studies/", response_model=Sequence[Study])
async def get_studies(catalog_id: str) -> Sequence[ORMStudy]:
    return repository.get_studies(catalog_id)

@secure.post("/studies/", status_code=201)
async def post_study(study: Study):
    try:
        repository.add_study(study)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return


@public.get("/samples/", response_model=Sequence[Sample])
async def get_samples(study_id: str) -> Sequence[ORMSample]:
    return repository.get_samples(study_id)

@secure.post("/samples/", status_code=201)
async def post_sample(sample: SampleCreateDTO):
    try:
        repository.add_sample(sample)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return


@public.get("/slides/", response_model=Sequence[Slide])
async def get_slides(sample_id: str) -> Sequence[ORMSlide]:
    return repository.get_slides(sample_id)

@secure.post("/slides/", status_code=201)
async def post_slide(slide: SlideCreateDTO):
    try:
        repository.add_slide(slide)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return


app.include_router(public)
app.include_router(secure)
