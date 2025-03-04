#!/bin/bash

DIR="$(dirname "$(readlink -f "$0")")"

cd "$DIR"

export PYTHONPATH="$dir"
export PYTHONUNBUFFERED=1

set -eux

pytest --cov=lymphocyte --cov-report term --cov-report "xml:$1"
