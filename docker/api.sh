#!/bin/bash

echo "Sleeping for 30 seconds…"
sleep 30

echo "Alembic migrations"
alembic upgrade head

cd api

gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000