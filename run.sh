# run.sh
#!/bin/bash
set -e
echo "📦 Loading environment variables..."
export $(grep -v '^#' .env | xargs)

if [ "$1" = "nolive" ]; then
    echo "🔧 Starting in 'nolive' mode..."
    docker compose -f ./docker-compose.nolive.yaml up --build
else
    echo "🧪 Starting in 'dev' mode with args: $@"
    docker compose -f ./docker-compose.yaml "$@"
fi
