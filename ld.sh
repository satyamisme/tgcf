#!/bin/bash
cd $(dirname $0)
sudo docker ps
sudo docker build . -t tgcf
sudo docker run -d --name tgcf -p 8501:8501 -v "$(pwd)/.env:/app/.env" -v "$(pwd)/tgcf.config.json:/app/tgcf.config.json" tgcf