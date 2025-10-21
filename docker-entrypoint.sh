#!/usr/bin/env bash
set -e
cd /app/backend
# If migrations or DB setup needed it can be added here.
exec "$@"
