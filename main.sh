#!/usr/bin/env bash
set -euo pipefail

# Build the site
python3 src/main.py

# Serve it
cd public
python3 -m http.server 8888
