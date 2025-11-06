#!/usr/bin/env bash
set -euo pipefail
uvicorn todo_backend.app.main:app --host 0.0.0.0 --port "$PORT"
