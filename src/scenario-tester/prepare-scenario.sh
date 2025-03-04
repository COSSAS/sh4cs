#!/bin/bash

set -ux
trap 'kill $(jobs -p)' INT EXIT SIGINT SIGTERM

(until kubectl port-forward deploy/test-app 8000 9090 9093 12345; do sleep 1; done) &
(until kubectl port-forward deploy/test-app2 8001:8000 12346:12345; do sleep 1; done) &
(until kubectl port-forward deploy/regeneration-demo 8002:8000 12347:12345; do sleep 1; done) &

wait
