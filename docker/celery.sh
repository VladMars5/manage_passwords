#!/bin/bash

cd api

if [[ "${1}" == "celery" ]]; then
  celery --app=celery_tasks.tasks:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=celery_tasks.tasks:celery flower
fi