#!/bin/sh

# Write the API base URL and catalog id to a configuration file that will be read by the client.
cat <<EOF > /usr/share/nginx/html/config.js
const API_BASE_URL = "$ROOT_PATH/api";
CATALOG_ID = "$CATALOG_ID";
EOF

# Substitute the environment variables in the nginx configuration template.
envsubst '$HTTP_PORT $ROOT_PATH $API_HOST' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
