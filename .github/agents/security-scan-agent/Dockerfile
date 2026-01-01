FROM python:3.12-slim

WORKDIR /agent

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agent/ ./agent/
COPY cli.py .
COPY manifest.yaml .

# Set entry point
ENTRYPOINT ["python", "cli.py"]
