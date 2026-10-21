#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================================="
echo " Starting Musubi 3D Studio v2.1.0 (HLD Compliant)..."
echo " Web UI available at: http://localhost:5151"
echo " Health check:        http://localhost:5151/health"
echo " Press Ctrl+C to stop."
echo "=========================================================="
python3 -m uvicorn musubi_web:app --host 0.0.0.0 --port 5151
