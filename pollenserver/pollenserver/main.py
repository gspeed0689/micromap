from typing import Dict, Optional, List

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from pydantic_settings import BaseSettings

from .mockupdatarepository import MockupDataRepository

# Default values. These values can also be set using environment variables.
class Settings(BaseSettings):
    max_results: int = 100
    default_order: str = 'abundance'


settings = Settings()

cors_origins = [
    "http://localhost:8081",# Development port. Required for Cross-Origin Resource Sharing (CORS)
    "http://localhost:8001",
]

def generate_unique_id(route: APIRoute):
    return f"{route.name}"


app = FastAPI(generate_unique_id_function=generate_unique_id)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repository = MockupDataRepository()


@app.get("/")
async def root():
    return {"message": "PollenBase API"}


@app.post("/submit/")
async def submit(family: Optional[str] = Query(default=None),
                 genus: Optional[str] = Query(default=None),
                 species: Optional[str] = Query(default=None),
                 study: Optional[str] = Query(default=None),
                 sample: Optional[str] = Query(default=None),
                 slide: Optional[str] = Query(default=None),
                 max_results: int = settings.max_results,
                 order: str = settings.default_order) -> Dict:
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
    # A genus may not be specific to a particular family, so the family must be given.
    if genus and not family:
        raise HTTPException(400, detail="A genus was requested, but the family was not provided")

    # A species may not be specific to a particular genus, so the genus must be given.
    if species and not genus:
        raise HTTPException(400, detail="A species was requested, but the genus was not provided")

    # Build search query

    if species:
        # TODO: Search on species level.
        pass
    elif genus:
        # TODO: Search on genus level.
        pass
    elif family:
        # TODO: Search on family level.
        pass
    else:
        # TODO: Search on database level.
        pass

    # TODO: return a dictionary with pollen id as key and a dictionary with pollen-info as value. The pollen info
    #  contains a low-resolution image, taxonomic info and study info. Other info can be queried using the pollen id.
    return {}


@app.get("/get-families/")
async def get_families() -> JSONResponse:
    return repository.get_families()


@app.get("/get-genera/")
async def get_genera(familyid: str) -> JSONResponse:
    return repository.get_genera(familyid)


@app.post("/get-species/")
async def get_species() -> List[str]:
    return []


@app.post("/get-study-info/")
async def get_study_info() -> List[str]:
    return []


@app.post("/get-sample-info/")
async def get_sample_info() -> List[str]:
    return []


@app.post("/get-slide-info/")
async def get_slide_info() -> List[str]:
    return []


@app.post("/get-slide/")
async def get_slide() -> Dict:
    # TODO: return (reference to - lazy loading?) whole-slide image and pollen-locations.
    return {}


@app.post("/get-pollen/")
async def get_pollen() -> Dict:
    # TODO: return full-resolution pollen image.
    return {}
