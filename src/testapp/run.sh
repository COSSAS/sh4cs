#!/bin/bash


DIR="$(dirname "$(readlink -f "$0")")"

cd "$DIR"

export PYTHONPATH="$dir"
export PYTHONUNBUFFERED=1


uvicorn main:app --reload --host 0.0.0.0 --port 8000
