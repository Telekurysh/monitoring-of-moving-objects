#!/usr/bin/env bash
# Simple script to run ApacheBench tests described in load_test_report.md
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost}

echo "Running GET test..."
ab -n 1000 -c 50 ${BASE_URL}/api/v1/objects

# echo "Running POST test..."
# ab -n 200 -c 10 -p tests/post_payload.json -T 'application/json' ${BASE_URL}/api/v1/objects
