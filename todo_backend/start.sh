#!/usr/bin/env bash
set -euo pipefail
mkdir -p /opt/render/project/.ca
if [ -n "${AIVEN_CA_B64:-}" ]; then
  echo "$AIVEN_CA_B64" | base64 -d > /opt/render/project/.ca/aiven-ca.pem
fi
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
