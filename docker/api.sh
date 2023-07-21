#!/bin/bash

echo "Sleeping for 30 seconds…"
sleep 30

echo "Alembic migrations"
alembic upgrade head

cd api

python main.py