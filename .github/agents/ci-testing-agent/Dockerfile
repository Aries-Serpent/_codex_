# Pinned base image for reproducibility
FROM python:3.12.3-slim

# Set working directory
WORKDIR /agent

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent/ ./agent/
COPY cli.py .
COPY manifest.yaml .

# Set entry point
ENTRYPOINT ["python", "cli.py"]
