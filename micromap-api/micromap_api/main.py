import os
from hashlib import sha256
from typing import Optional, List, Dict

from fastapi import FastAPI, Query, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute, APIRouter
from fastapi.security import APIKeyHeader

from .exceptions import KeyViolationException, EntityDoesNotExistException

from .postgresqldatarepository import PostgresqlDataRepository
from .models import CatalogBase, Catalog, FamilyBase, Family, Genus, GenusBase, Species, SpeciesBase, ItemCreateDTO, Item, settings, Study, Sample, Slide, SampleCreateDTO, SlideCreateDTO


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
async def root():
    return {"message": "MicroMap API"}


@public.get("/items/")
async def items(family: Optional[str] = Query(default=None),
                genus: Optional[str] = Query(default=None),
                species: Optional[str] = Query(default=None),
                is_include_non_reference_check: bool = Query(default=True),
                max_results: int = settings.max_results,
                type_user_max_results: int = Query(default=100),
                study: Optional[str] = Query(default=None),
                sample: Optional[str] = Query(default=None),
                slide: Optional[str] = Query(default=None),
                order: str = settings.default_order,
                page: int = Query(default=1),
                is_include_if_genus_is_type: bool = Query(default=True),
                is_include_if_species_is_type: bool = Query(default = True)
                ) -> List[Item]:
    """
    Use:
    This function get the items we use to show the thumbnails
    users arguments specified by the user.
    The function is returns according to the highest taxonomic detail specified by the user
        species
        genus
        family

    Offset and typesetting are performed here before the get_items function is called

    Expaination of params:
    Handles a new query for pollen images.

    :param family: A specific pollen family.
    :param genus: A specific genus of a family.
    :param species: A specific species of a genus.
    :param study: A specific study.
    :param sample: A specific sample in a study.
    :param slide: A specific slide in a sample.
    :param max_results: Maximum number of results returned.
    :param order: The order in which the results are returned.
    :return: A dictionary with matches.
    """
    # Build search query
    #ensure the user doesnt put in a number greater than what is allowed in env settings
    if type_user_max_results > max_results:
        type_user_max_results = max_results#

    # Calculate offset
    offset = (page - 1) * type_user_max_results

    # Fetch results based on available filters
    if species:
        return repository.get_items(species_id=species, user_max_results = type_user_max_results, include_non_reference=is_include_non_reference_check, offset =offset, is_include_if_species_is_type = is_include_if_species_is_type)
        pass
    elif genus:
        return repository.get_items(genus_id=genus, user_max_results = type_user_max_results, include_non_reference =is_include_non_reference_check, offset = offset, is_include_if_genus_is_type = is_include_if_genus_is_type)
    elif family:
        return repository.get_items(family_id=family, user_max_results = type_user_max_results,  include_non_reference =is_include_non_reference_check, offset = offset)
    else:
        # TODO: Search on database level.
        pass

    return {}


@public.get("/catalogs/")
async def catalog() -> List[Catalog]:
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


@public.get("/families/")
async def families(catalog_id: str) -> List[Family]:
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


@public.get("/genera/")
async def genera(family_id: str, is_include_if_genus_is_type: bool = True) -> List[Dict]:
    '''
    Used for alphabetsearch and genera drop down additional argument to not include genera_is_type
    '''
    return repository.get_genera(family_id, is_include_if_genus_is_type)

#not use
@public.get("/genera_for_alphabetical/")
def get_genera_for_alphabetica():
    data = repository.get_all_genera()  # No need for 'self'
    return data

#not used
@secure.post("/genera/", status_code=201)
async def post_genus(genus: GenusBase):
    return { "id": repository.add_genus(genus) }

#not used
@secure.put("/genera/", status_code=200, responses = {404: {"description": "Genus does not exist"}})
async def put_genus(genus: Genus):
    try:
        repository.update_genus(genus)
    except EntityDoesNotExistException:
        return 404
    return


@public.get("/species/")

async def species(genera_id: Optional[str] = None, catalog_id: Optional[str] = None) -> List[Species]:
    ''' returns species according to genus_id used in species drop down and alphabetical search'''
    if genera_id:
        return repository.get_species(genera_id)
    if catalog_id:
        return repository.get_species_for_catalog(catalog_id)
#not used
@secure.post("/species/", status_code=201)
async def post_species(species: SpeciesBase):
    return { "id": repository.add_species(species) }
#not used
@secure.put("/species/", status_code=200, responses = {404: {"description": "Species does not exist"}})
async def put_species(species: Species):
    try:
        repository.update_species(species)
    except EntityDoesNotExistException:
        return 404
    return


@secure.post("/items/")
async def post_item(item: ItemCreateDTO) -> int:
    repository.add_item(item)
    return 200

@public.get("/studies/")
async def studies(catalog_id: str) -> List[Study]:
    return repository.get_studies(catalog_id)

@secure.post("/studies/", status_code=201)
async def post_study(study: Study):
    try:
        repository.add_study(study)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return

@public.get("/samples/")
async def samples(study_id: str) -> List[Sample]:
    return repository.get_samples(study_id)

@secure.post("/samples/", status_code=201)
async def post_sample(sample: SampleCreateDTO):
    try:
        repository.add_sample(sample)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return

@public.get("/slides/")
async def slides(sample_id: str) -> List[Slide]:
    return repository.get_slides(sample_id)

@secure.post("/slides/", status_code=201)
async def post_slide(slide: SlideCreateDTO):
    try:
        repository.add_slide(slide)
    except KeyViolationException as e:
        raise HTTPException(status_code=409, detail=e.detailed_message)
    return

@public.get("/genera/letter/{letter}")
async def genera_by_letter(letter: str, is_include_if_genus_is_type: bool = True):
    '''Return GENERA by capital first letter, for alphabetical search, removes if_genyus_is_type'''
    genera_list = repository.get_genera_by_letter(letter, is_include_if_genus_is_type)
    return genera_list

#not used
@public.get("/family/letter/{letter}")
async def family_by_letter(letter: str):
    family_list = repository.get_family_by_letter(letter)

    return family_list

#Dashbaord test - functions written for the future.
#Family
@public.get("/get_family_count/")
async def get_family_count_endpoint():
    num =  repository.get_family_count()
    return {"family_count": num}
#Genera
@public.get("/get_genera_count/")
async def get_genera_count_endpoint():
    num =  repository.get_genera_count()
    return {"Genera": num}

#Species
@public.get("/get_species_count/")
async def get_species_count_endpoint():
    num =  repository.get_species_count()
    return {"species_count": num}
# #subspecies
#study post
#sample get/post
#slide get/post


app.include_router(public)
app.include_router(secure)
