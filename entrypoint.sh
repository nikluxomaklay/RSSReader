#!/bin/bash -e

if [[ "$ENTRY_POINT" = "app" ]]; then
    echo "Starting RSSReader"
    uv run python ./main.py

elif [[ "$ENTRY_POINT" = "migrations" ]]; then
    echo "Running migrations"
    uv run alembic upgrade head
else
    exec "$@"
fi