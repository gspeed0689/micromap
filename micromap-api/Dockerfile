FROM python:3.9-slim

# Copy and build and install the API.
RUN --mount=type=bind,target=/src,source=./,rw=true \
    --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    pip install --no-cache-dir -r /src/requirements.txt && \
    pip install --no-cache-dir gunicorn && \
    pip install /src

ENV PGHOSTADDR=localhost
ENV PGDATABASE=micromap
ENV PGUSER=postgres
ENV PGPASSWORD=postgres
ENV PGPORT=5432

EXPOSE 8000
HEALTHCHECK --timeout=3s --start-period=30s CMD curl -f http://localhost:8000/

# Run gunicorn -k uvicorn.workers.UvicornWorker for production. Bind on IPv4 and IPv6.
ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "micromap_api.main:app", "--workers", "4", "--bind", "[::]:8000"]

LABEL org.opencontainers.image.source="https://github.com/umcu-isi/micromap"
LABEL org.opencontainers.image.vendor="Image Sciences Institute, University Medical Center Utrecht"
LABEL org.opencontainers.image.description="MicroMap API"
