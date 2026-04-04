#!/usr/bin/env sh
celery -A app.core.celery_app.celery_app worker --loglevel=info
