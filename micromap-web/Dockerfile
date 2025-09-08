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
    npm install && \
    npx openapi --input ./openapi.json --output ./src/typescript/client --client axios && \
    npx tailwindcss -i ./src/css/style.css -o ./css/micromap.css && \
    npx webpack && \
    mkdir /html && \
    cp -r /src/dist /src/css /src/index.html /html/

# Build the final nginx container image. Configuration and cache folders should be writeable by the root group for in
# OpenShift.
FROM nginx:stable-alpine-slim
COPY --from=builder /html/ /usr/share/nginx/html/
COPY --chmod=775 ./write-config.sh /docker-entrypoint.d/
COPY default.conf.template /etc/nginx/conf.d/
RUN chmod -R g+rwX /usr/share/nginx/html && \
    chmod -R g+rwX /etc/nginx/conf.d && \
    chmod -R g+rwX /var/cache/nginx && \
    chmod -R g+rwX /run

LABEL org.opencontainers.image.source="https://github.com/umcu-isi/micromap"
LABEL org.opencontainers.image.vendor="Image Sciences Institute, University Medical Center Utrecht"
LABEL org.opencontainers.image.description="MicroMap web server"
