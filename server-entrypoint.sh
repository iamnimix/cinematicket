#!/bin/sh

until cd /app
do
    echo 'Waiting for server volume...'
done

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done

python manage.py collectstatic --noinput

daphne -b 0.0.0.0 -p 8000 core.asgi:application