import setuptools

setuptools.setup(
    name="micromap-api",
    version="0.0.1",
    author="Edwin Bennink",
    author_email="H.E.Bennink@umcutrecht.nl",
    description="MicroMap API module",
    packages=['micromap_api'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Development Status :: 2 - Pre-Alpha"
    ],
    python_requires='>=3.9',
    install_requires=[
        'fastapi~=0.100.1',
        'uvicorn~=0.23.2',
        'pydantic~=2.1.1',
        'pydantic-settings~=2.0.3',
        'sqlalchemy~=2.0.23',
        'psycopg2-binary~=2.9.9'
    ],
    extras_require={
        'asgi webserver': ['uvicorn~=0.20.0'],
        'wsgi support': ['a2wsgi~=1.7.0'],
    }
)
