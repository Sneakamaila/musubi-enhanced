FROM python:3.11-slim-bookworm

LABEL maintainer="Sneakamaila"
LABEL version="2.2.0"
LABEL description="Musubi 3D Studio - High-Fidelity 3D Video Generator for Looking Glass Musubi"

ENV APP_VERSION=2.2.0

# Install system dependencies (ffmpeg, libgl for opencv, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Depth-Anything-V2 ONNX model during build
RUN mkdir -p /app/models && \
    curl -L -o /app/models/depth_anything_v2_vits.onnx \
    https://huggingface.co/yuvraj108c/Depth-Anything-2-Onnx/resolve/main/depth_anything_v2_vits.onnx

# Copy source code and UI assets
COPY musubi_core.py musubi_web.py musubi_cli.py /app/
COPY static /app/static/

# Create working directories
RUN mkdir -p /app/uploads /app/outputs

# Persistent volumes for Unraid / Docker
VOLUME ["/app/outputs", "/app/uploads", "/app/models"]

# Environment defaults
ENV HOST=0.0.0.0
ENV PORT=5151
ENV PYTHONUNBUFFERED=1

EXPOSE 5151

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:5151/health || exit 1

CMD ["python3", "musubi_web.py"]
