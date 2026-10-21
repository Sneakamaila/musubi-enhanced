#!/bin/bash
cd "$(dirname "$0")"
echo "=========================================================="
echo " Starting Musubi 3D Studio..."
echo " Web UI available at: http://localhost:8080"
echo " Press Ctrl+C to stop."
echo "=========================================================="
python3 -m uvicorn musubi_web:app --host 0.0.0.0 --port 8080
