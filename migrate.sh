#!/bin/bash
set -e

# --- SETTINGS ---
# Using example: ./migrate.sh "migration_description"
# File name (example: docker-compose.dev.yml):
COMPOSE_FILE="docker-compose.dev.yml"

# User and database host (from your .env or compose)
DB_USER="shinobi"
DB_HOST="postgres_db"

# 1. Automatic transition to the folder where the script itself is located
# This ensures that docker compose finds the file next to the script
cd "$(dirname "$0")" || { echo "Error: Failed to navigate to script directory"; exit 1; }

# 2. Argument checking (migration description)
if [ -z "$1" ]; then
  echo "Error: Please enter a migration description!"
  echo "Example: ./migrate.sh 'remove_email_field'"
  exit 1
fi

MESSAGE=$1

# 3. Checking the presence of a configuration file
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Error: File $COMPOSE_FILE not found in directory $(pwd)!"
  exit 1
fi

# 4. Raising the base
echo "[DEV] Starting database $COMPOSE_FILE..."
docker compose -f "$COMPOSE_FILE" up "$DB_HOST" -d

# 5. Waiting ready Postgres
echo "Waiting for Postgres to wake up..."
until docker compose -f "$COMPOSE_FILE" exec "$DB_HOST" pg_isready -U "$DB_USER" > /dev/null 2>&1; do
  echo -n "."
  sleep 1
done
echo -e "\nDatabase is ready."

# 6. Creating migration
echo "Generating a migration file..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps bot alembic revision --autogenerate -m "$MESSAGE" || { echo "Generation error!"; exit 1; }

# 7. TEST_DRIVE: Checking the stability of the migration
echo "Running a migration test (Test Drive)..."

echo "  -> 1/3 Upgrade (Upgrade head)..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps bot alembic upgrade head || { echo "Application error!"; exit 1; }

echo "  -> 2/3 Rollback (Downgrade -1)..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps bot alembic downgrade -1 || { echo "Rollback error! Check the downgrade() method in the migration file"; exit 1; }

echo "  -> 3/3 Final upgrade..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps bot alembic upgrade head || { echo "Final application error!"; exit 1; }

# 8. Checking for "forgotten" fields in models
echo "Checking the compliance of models and database (alembic check)..."
docker compose -f "$COMPOSE_FILE" run --rm --no-deps bot alembic check || { echo "Attention: Models do not match current migrations!"; exit 1; }

# 9. Stopping base
echo "Stopping the base..."
docker compose -f "$COMPOSE_FILE" stop "$DB_HOST"

echo "--------------------------------------------------"
echo "Migration '$MESSAGE' created, tested and applied."
echo "Check correctness migration file in folder alembic/versions/"
