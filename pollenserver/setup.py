import setuptools

setuptools.setup(
    name="pollenserver",
    version="0.0.1",
    author="Edwin Bennink",
    author_email="H.E.Bennink@umcutrecht.nl",
    description="PollenBase API module",
    packages=['pollenserver'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Development Status :: 2 - Pre-Alpha"
    ],
    python_requires='>=3.8',
    install_requires=[
        'fastapi>=0.88.0',
        'pydantic>=1.10.2',
    ],
    extras_require={
        'asgi webserver': ['uvicorn>=0.20.0'],
        'wsgi support': ['a2wsgi>=1.7.0'],
    }
)
