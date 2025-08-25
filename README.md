# MicroMap Server
MicroMap is designed to access image (stacks) at different taxonomic levels.
The project was initially envisioned for microscopic pollen data, but the long-term goal is to expand its use to other
domains, such as medical imagery.

## Setting up a Development Environment
This README is specific to the pollen use case and is intended for users setting up MicroMap for development. 

### MicroMap Overview
MicroMap consists of three main components:
1. Database: A PostgreSQL database stores pollen information in a hierarchical format.  
   **ToDo:** Add a description of the database structure/schema.  
2. REST API: The [REST API](https://en.wikipedia.org/wiki/REST) translates user queries made on the MicroMap website
   into SQL queries that interact with the database. The REST API is implemented using FastAPI.
3. MicroMap Website: The website serves as the Graphical User Interface (GUI) and it built with TypeScript.
   It allows users to query and view pollen images at various taxonomic levels and scroll through 3D image stacks. 

### Prerequisites
Before setting up the development environment, ensure the following software is installed:  
- [Docker](https://www.docker.com/): Used to run the PostgreSQL database server.
- [DBeaver](https://dbeaver.io/): Used access the database.
- [PyCharm (Community Edition)](https://www.jetbrains.com/toolbox-app/)  
- Python 3.9

### Environment files
The `.env` contains the database and API server configuration. At least set a new database password and API key hash.

An SHA-256 hash for `api_key` can be calculated with:
```python
from hashlib import sha256
sha256(api_key.encode()).hexdigest()
```

### Set Up a PostgreSQL Docker Container
A Docker container includes everything needed to run an application (e.g. runtime, system tools, libraries, and
settings).
To run the PostgreSQL container as configured in `docker-compose.yml`, change directory to where this file located is and run:
```shell
docker-compose --env-file .env up -d
```
When run for the first time, the `micromap` database will be empty. The REST API will create new tables and relations.
It will not attempt to recreate tables already present.

### Run the REST API
Optionally create and start a [Python virtual environment](https://docs.python.org/3/library/venv.html) for this project.   
Install the requirements for development:
```shell
python -m pip install -r micromap-api/requirements.txt
```
Install the `micromap-api` package in editable mode:
```shell
python -m pip install -e ./micromap-api
```
Run the webserver using [uvicorn](https://www.uvicorn.org/):
```shell
uvicorn --env-file .env micromap_api.main:app
```
If successful, the terminal should output a link that can be used in the web browser to access the REST API, for example `http://localhost:8000/`.
The endpoint /docs, e.g. `http://localhost:8000/docs` should show the OpenAPI documentation.


## Website

### Install npm
Compiling the source code for the website requires the node package manager (npm) and build tools.

In Windows, the node version manager npv can be installed using [Chocolatey](https://chocolatey.org/):
```shell
choco install nvm
```
Then restart the shell and install and activate the latest npm version:
```shell
nvm install latest
nvm use latest
```

### Install dependencies
To install all dependencies defined in `package.json`, run this command from the `wwwroot` directory:
```shell
npm install
```

### Generate the OpenAPI client module
An [axios](https://axios-http.com/) client should be generated using the command below (run from the `wwwroot` directory). In case the Micromap API is changed, the client should be re-generated.
*Note: This requires a running micromap_api webserver. See above.*
```shell
npm run generate-client
```

### Generate CSS
To compile the tailwind-annotated css, run this command in the `wwwroot` directory: 
```bash
npx tailwindcss -i ./src/css/style.css -o ./css/pollenbase.css
```
*You can add **--watch** to hot rebuild based on changes in the source files.*

### Compile the client module
To compile the typescript source files to a javascript bundle, run this command in the `wwwroot` directory:
```bash
npx webpack
```
*You can add **--watch** to hot rebuild based on changes in the source files.*
