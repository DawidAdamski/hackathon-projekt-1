#!/usr/bin/env sh
set -e

celery -A app.celery_app.celery_app beat -l info
