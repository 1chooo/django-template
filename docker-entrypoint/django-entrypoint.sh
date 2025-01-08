#!/bin/sh

if [ -z "$SERVER_HOST" ]; then
   SERVER_HOST=127.0.0.1
fi
if [ -z "$SERVER_PORT" ]; then
   SERVER_PORT=8000
fi

python manage.py collectstatic --noinput
python -m uvicorn config.asgi:application --host=$SERVER_HOST --port=$SERVER_PORT

exec "$@"
