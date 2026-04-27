#!/bin/sh
set -eu

docker exec n8n node -e 'console.log(require.resolve("better-sqlite3"))'
