#!/bin/sh

python manage.py migrate
python -m uvicorn config.asgi:application

exec "$@"
