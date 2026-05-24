#!/bin/bash

CONTAINER_NAME="my-postgres"

# 1. Check if the container is already running perfectly
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "✅ Database is already running on port 5432!"
    exit 0
fi

# 2. Check if the container exists but is stopped
if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
    echo "🚀 Waking up your existing database container..."
    docker start $CONTAINER_NAME
else
# 3. If it doesn't exist at all, build it fresh
    echo "✨ Creating and starting a new database container..."
    docker run --name $CONTAINER_NAME \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=smart_triage_db \
      -p 5432:5432 \
      -d postgres
fi

echo "🎉 Database is ready! You can now start Streamlit."
