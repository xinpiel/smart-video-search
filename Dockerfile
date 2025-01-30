# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies into /app/venv and cleanup
RUN python -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    find /app/venv -type d -name "__pycache__" -exec rm -r {} + && \
    find /app/venv -type d -name "*.dist-info" -exec rm -r {} + && \
    find /app/venv -type d -name "*.egg-info" -exec rm -r {} +

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy only the necessary files from builder
COPY --from=builder /app/venv /app/venv
COPY test_app.py .
COPY requirements.txt .

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Make port 8080 available
EXPOSE 8080

# Run streamlit
CMD ["streamlit", "run", "test_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true", "--server.runOnSave=false"] 