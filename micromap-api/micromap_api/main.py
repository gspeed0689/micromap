import os
from hashlib import sha256
from typing import Optional, List

from fastapi import FastAPI, Query, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute, APIRouter
from fastapi.security import APIKeyHeader

from .exceptions import KeyViolationException, EntityDoesNotExistException

from .postgresqldatarepository import PostgresqlDataRepository
from .models import CategoryBase, Category, FamilyBase, Family, Genus, GenusBase, Species, SpeciesBase, ItemCreateDTO, Item, settings, Study, Sample, Slide, SampleCreateDTO, SlideCreateDTO


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
                study: Optional[str] = Query(default=None),
                sample: Optional[str] = Query(default=None),
                slide: Optional[str] = Query(default=None),
                max_results: int = settings.max_results,
                order: str = settings.default_order) -> List[Item]:
    """
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

    print('/items', family, genus)
    if species:
        # TODO: Search on species level.
        pass
    elif genus:
        return repository.get_items(genus_id=genus, include_non_reference =is_include_non_reference_check)
    elif family:
        return repository.get_items(family_id=family, include_non_reference =is_include_non_reference_check)
    else:
        # TODO: Search on database level.
        pass

    # TODO: return a dictionary with pollen id as key and a dictionary with pollen-info as value. The pollen info
    #  contains a low-resolution image, taxonomic info and study info. Other info can be queried using the pollen id.
    return {}


@public.get("/categories/")
async def category() -> List[Category]:
    return repository.get_categories()

@secure.post("/categories/", status_code=201)
async def post_category(category: CategoryBase):
    return { "id": repository.add_category(category) }

@secure.put("/categories/", status_code=200, responses = {404: {"description": "Category does not exist"}})
async def put_category(category: Category):
    try:
        repository.update_category(category)
    except EntityDoesNotExistException:
        return 404
    return


@public.get("/families/")
async def families(category_id: str) -> List[Family]:
    return repository.get_families(category_id)

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
async def genera(family_id: str) -> List[Genus]:
    return repository.get_genera(family_id)

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


@public.get("/species/")
async def species(genera_id: Optional[str] = None, category_id: Optional[str] = None) -> List[Species]:
    if genera_id:
        return repository.get_species(genera_id)
    if category_id:
        return repository.get_species_for_category(category_id)

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


@secure.post("/items/")
async def post_item(item: ItemCreateDTO) -> int:
    repository.add_item(item)
    return 200

@public.get("/studies/")
async def studies(category_id: str) -> List[Study]:
    return repository.get_studies(category_id)

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

#return GENERA by capital first letter
@public.get("/genera/letter/{letter}")
async def genera_by_letter(letter: str):
    genera_list = repository.get_genera_by_letter(letter)
    return [
        {"id": str(genus.id), "name": genus.name}
        for genus in genera_list
    ]

#return FAMILY by capital first letter
@public.get("/family/letter/{letter}")
async def family_by_letter(letter: str):
    family_list = repository.get_family_by_letter(letter)

    return family_list
# #subspecies
#study post
#sample get/post
#slide get/post


app.include_router(public)
app.include_router(secure)
