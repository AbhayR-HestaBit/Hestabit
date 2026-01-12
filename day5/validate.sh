#!/bin/sh


echo "running validation..."

npm run lint
npm run format:check

echo "validation passed"
