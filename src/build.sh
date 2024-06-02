#!/bin/bash

git pull
docker build -t fheonix/rag-app:0.0.3 .
docker push fheonix/rag-app:0.0.3