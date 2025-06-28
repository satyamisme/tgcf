#!/bin/bash
# Script to stop and remove the tgcf container

CONTAINER_NAME="my-tgcf-container"

# Check if container exists (running or stopped)
# The `grep -q` makes it silent and just sets exit status.
if ! docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Container '${CONTAINER_NAME}' does not exist."
    exit 0
fi

echo "Stopping container '${CONTAINER_NAME}'..."
docker stop "${CONTAINER_NAME}"
if [ $? -eq 0 ]; then
    echo "Container '${CONTAINER_NAME}' stopped."
else
    # If stop fails, it might already be stopped or another issue occurred.
    # We'll proceed to try and remove it anyway.
    echo "WARN: Could not stop container '${CONTAINER_NAME}' (it might have already been stopped)."
fi

echo "Removing container '${CONTAINER_NAME}'..."
docker rm "${CONTAINER_NAME}"
if [ $? -eq 0 ]; then
    echo "Container '${CONTAINER_NAME}' removed."
else
    echo "WARN: Could not remove container '${CONTAINER_NAME}'. It might have already been removed." >&2
    # Don't exit with error if removal fails after a successful stop, as it might be already gone
    # or if stop failed and it was never running.
fi
