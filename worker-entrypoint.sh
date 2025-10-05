#!/bin/sh


until cd /app
do
  echo "Waiting for server volume..."
done

python -m celery -A core worker -l info