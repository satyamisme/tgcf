#!/bin/bash
# Script to start the tgcf container

CONTAINER_NAME="my-tgcf-container"
IMAGE_NAME="tgcf-image"
ENV_FILE=".env"
CONFIG_FILE="tgcf.config.json"
# Assuming tgcf-web is the target, exposing port 8501.
# If running tgcf CLI (live/past) without a web server, remove EXPOSE_PORT line and its usage.
EXPOSE_PORT="-p 8501:8501"

# Ensure script is run from its directory to correctly find .env and tgcf.config.json
# and ensure paths for volume mounts are correct.
cd "$(dirname "$0")" || exit 1

if [ ! -f "${ENV_FILE}" ]; then
    echo "ERROR: Environment file '${ENV_FILE}' not found in $(pwd)." >&2
    echo "Please create it before starting the container."
    exit 1
fi

if [ ! -f "${CONFIG_FILE}" ]; then
    echo "ERROR: Configuration file '${CONFIG_FILE}' not found in $(pwd)." >&2
    echo "Please create it before starting the container."
    exit 1
fi

# Check if image exists
if ! docker image inspect "${IMAGE_NAME}" &> /dev/null; then
    echo "ERROR: Docker image '${IMAGE_NAME}' not found." >&2
    echo "Please build it first using ./build-image.sh"
    exit 1
fi

# Check if container is already running
if [ "$(docker ps -q -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Container '${CONTAINER_NAME}' is already running."
    docker ps -f name=^/${CONTAINER_NAME}$
    exit 0
fi

# Check if container exists but is stopped, then remove it
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Container '${CONTAINER_NAME}' exists but is stopped. Removing it first..."
    docker rm "${CONTAINER_NAME}"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to remove existing stopped container '${CONTAINER_NAME}'." >&2
        exit 1
    fi
fi

echo "Starting container '${CONTAINER_NAME}' from image '${IMAGE_NAME}'..."
# The /app/ path for mounted files is a common convention.
# Ensure your Dockerfile's WORKDIR is /app or tgcf is configured to find these files at /app/.
docker run -d \
  --name "${CONTAINER_NAME}" \
  --env-file "${ENV_FILE}" \
  -v "$(pwd)/${CONFIG_FILE}:/app/${CONFIG_FILE}" \
  ${EXPOSE_PORT} \
  "${IMAGE_NAME}"

if [ $? -eq 0 ]; then
    echo "Container '${CONTAINER_NAME}' started successfully."
    if [ -n "${EXPOSE_PORT}" ]; then
         echo "Web UI (if active) should be accessible on port 8501 of the host."
    fi
    echo "View logs with: ./view-logs.sh"
else
    echo "ERROR: Failed to start container '${CONTAINER_NAME}'." >&2
    echo "Attempting to show logs from failed container start:"
    docker logs "${CONTAINER_NAME}" # Show logs on failure
    exit 1
fi
