#!/bin/bash

if [ "$1" == "runserver" ]; then
    export DJANGO_SETTINGS_MODULE=app.settings

    echo Start Gunicorn ...
    exec gunicorn app.wsgi:application --name app --bind 0.0.0.0:8000 --workers 6 --log-level=info -t 600 --capture-output
fi

if [ "$1" == "migrate" ]; then
    echo "Running migrations"
    # Apply database migrations
    python3 manage.py "$@"
fi

if [ "$1" == "collectstatic" ]; then
    echo "Running collectstatic"
    # Apply collectstatic
    python3 manage.py "$@" --noinput -c
fi

if [ "$1" == "workers" ]; then
    echo "Running celery"
    # Apply run celery
   exec celery -A app worker -l info -E --concurrency=3 -n worker@%h
fi