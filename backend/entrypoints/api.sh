#!/usr/bin/env sh
set -e

# opcjonalnie – żeby backend startował już po migracjach
# alembic upgrade head || true

uvicorn app.main:app --host 0.0.0.0 --port 8000
