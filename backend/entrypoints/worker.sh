#!/usr/bin/env sh
set -e

celery -A app.celery_app.celery_app worker -l info -Q fast,fail,slow,celery
