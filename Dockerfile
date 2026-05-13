# GSH Pipeline Container - Hybrid AWS Deployment
# Based on report: https://github.com/[org]/gsh-pipeline
# Versions: Docker 20.10+, Python 3.9, BEDOPS 2.4.39, BEDTools 2.30

FROM python:3.9-slim-bullseye

LABEL maintainer="GSH Pipeline Team"
LABEL description="Containerized Genomic Safe Harbor Pipeline with BEDOPS and BEDTools"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies including BEDOPS and BEDTools
RUN apt-get update && apt-get install -y \
    bedops=2.4.39+dfsg-1 \
    bedtools=2.30.0-1 \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy pipeline requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline code
COPY . .

# Create output directory
RUN mkdir -p /data/output /data/input

# Set environment variables for genomic tools
ENV BEDOPS_TOOLSET=/usr/bin
ENV BEDTOOLS_TOOLSET=/usr/bin
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command - run main pipeline
CMD ["python", "main.py"]
