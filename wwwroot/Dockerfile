# Generate the OpenAPI JSON schema.
ARG API_IMAGE
FROM ${API_IMAGE} AS api

COPY ./export_api.py /tmp/
RUN cd /tmp && \
    BUILD_MODE=1 python ./export_api.py

# Build the website and copy it to /html
FROM node:slim AS builder
COPY --from=api /tmp/openapi.json /src/
COPY ./ /src/
RUN cd /src && \
    npx openapi --input ./openapi.json --output ./src/typescript/client --client axios && \
    npx tailwindcss -i ./src/css/style.css -o ./css/pollenbase.css && \
    npx webpack && \
    mkdir /html && \
    cp -r /src/dist /src/css /src/index.html /src/config.js /html/

# Build the final nginx container image.
FROM nginx:stable-alpine-slim
COPY --from=builder /html/ ./src/config.js /usr/share/nginx/html/

HEALTHCHECK --timeout=3s --start-period=30s CMD wget -O /dev/null http://localhost || exit 1
