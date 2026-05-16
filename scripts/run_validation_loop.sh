#!/usr/bin/env sh
set -eu

LOOPS="${1:-3}"
TASK_SPEC="${2:-examples/phase3_task.dry_run.json}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"
mkdir -p runtime

i=1
while [ "$i" -le "$LOOPS" ]; do
  echo "== loop ${i}: unit tests =="
  python3 -m unittest discover -s tests
  echo "== loop ${i}: phase3 smoke =="
  python3 scripts/run_phase3_loop.py "$TASK_SPEC" --out "runtime/phase3_result_remote_loop${i}.json"
  i=$((i + 1))
done

echo "validation_loops_completed=${LOOPS}"
