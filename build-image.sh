#!/bin/bash
# Script to build the Docker image for tgcf
# Image will be named 'tgcf-image'

echo "Building Docker image 'tgcf-image' from Dockerfile in current directory..."
docker build -t tgcf-image .

if [ $? -eq 0 ]; then
    echo "Docker image 'tgcf-image' built successfully."
else
    echo "ERROR: Docker image build failed." >&2
    exit 1
fi
