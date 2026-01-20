# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

# Install system dependencies for Postgres and YOLO
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose FastAPI and Dagster ports
EXPOSE 8000 3000

# Default CMD (can be overridden by docker-compose)
CMD ["bash"]
