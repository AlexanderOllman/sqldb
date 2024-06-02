#!/bin/bash

echo "Pulling latest..."
git pull

echo "Building image..."
docker build -t fheonix/rag-app:0.0.3 .

echo "Pushing image..."
docker push fheonix/rag-app:0.0.3

echo "Done."