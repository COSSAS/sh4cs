#!/bin/bash

DIR="$(dirname "$(readlink -f "$0")")"

cd "$DIR"

export PYTHONPATH="$dir"
export PYTHONUNBUFFERED=1

RC=0
trap 'RC=1' ERR
set -ux

pylint "$PWD/**/*.py" --output-format colorized
mypy --no-install-types --pretty .
black --check .
isort --check .

exit $RC
