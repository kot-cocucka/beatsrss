#!/bin/sh
set -e


# Load environment variables from .env file
export $(cat .env | xargs)

# Wait for the PostgreSQL service to be available
until pg_isready --host="$POSTGRES_HOST" --dbname="$POSTGRES_DB" --username="$POSTGRES_USER"
do
  echo "Waiting for PostgreSQL to be available..."
  sleep 1
done

cd /app/

case "$1" in
    bot)
      exec python main.py
    ;;
    celery)
        celery -A tasks.tasks worker --loglevel=INFO

    ;;
    *)
        exec $@
    ;;
esac
