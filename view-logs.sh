#!/bin/bash
# Script to view logs from the tgcf container

CONTAINER_NAME="my-tgcf-container"

# Check if container exists (running or stopped)
# The `grep -q` makes it silent and just sets exit status.
if ! docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Container '${CONTAINER_NAME}' does not exist." >&2
    echo "Try starting it first with ./start-container.sh"
    exit 1
fi

if [ "$1" == "--all" ]; then
    docker logs "${CONTAINER_NAME}"
else
    echo "Tailing logs for '${CONTAINER_NAME}'. Press Ctrl+C to stop."
    docker logs -f "${CONTAINER_NAME}"
fi
