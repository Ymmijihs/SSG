#!/usr/bin/env bash
set -euo pipefail

# Try to infer REPO_NAME from the origin URL
REPO_URL="$(git remote get-url --push origin 2>/dev/null || true)"
if [[ -z "${REPO_URL}" ]]; then
  echo "Could not detect git remote 'origin'. Falling back to hardcoded name."
  REPO_NAME="REPO_NAME"   # <- change this if needed
else
  REPO_NAME="$(basename "${REPO_URL}" .git)"
fi

BASEPATH="/${REPO_NAME}/"
echo "[BUILD] Using basepath: ${BASEPATH}"

python3 src/main.py "${BASEPATH}"
