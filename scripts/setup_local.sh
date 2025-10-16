#!/bin/bash
echo "🚀 Setup local environment"
if ! command -v docker &> /dev/null; then
    echo "Docker not installed"
    exit 1
fi
echo "Starting Docker..."
docker-compose up -d
echo "Done!"
