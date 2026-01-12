#!/bin/bash
set -e

echo "running validation..."

node -c server.js
npx eslint .
npx prettier --check .

echo "validation passed"
