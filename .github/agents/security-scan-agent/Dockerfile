# FROM python:3.12-slim (pinned below)
FROM python:3.12-slim@sha256:090ba77e2958f6af52a5341f788b50b032dd4ca28377d2893dcf1ecbdfdfe203

# Metadata
LABEL maintainer="codex-ml-team"
LABEL org.opencontainers.image.description="Security Scan Agent for Codex"
LABEL org.opencontainers.image.version="1.0.0"

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

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash agent && \
    chown -R agent:agent /agent

# Switch to non-root user
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Set entry point
ENTRYPOINT ["python", "cli.py"]
