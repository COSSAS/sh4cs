#!/bin/bash


DIR="$(dirname "$(readlink -f "$0")")"

cd "$DIR"

export PYTHONPATH="$dir"
export PYTHONUNBUFFERED=1

# export OTEL_PYTHON_LOG_CORRELATION=true
# export OTEL_PYTHON_LOG_LEVEL=info
export OTEL_LOGS_EXPORTER=none
export OTEL_METRICS_EXPORTER=none
export OTEL_TRACES_EXPORTER=none

export OTEL_SERVICE_NAME=lymphocyte

export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=12345

# watchmedo auto-restart --pattern="*.py;*.yml;*.yaml" --recursive --debounce-interval 1 flask -- run

cd ..
export LYMPHOCYTE_CONFIG="lymphocyte/settings.yaml"
export LYMPHOCYTE_LOG_CONFIG="lymphocyte/logging-rich.ini"
# export PYTHONASYNCIODEBUG=1

watchmedo auto-restart --pattern="*.py;*.yml;*.yaml;*.toml" --recursive --debounce-interval 1 \
    hypercorn -- \
    'lymphocyte.main:app' \
    --bind 0.0.0.0:12345 \
    --log-config "$LYMPHOCYTE_LOG_CONFIG" \
    --debug
