# Single stage build for faster completion
FROM python:3.11-slim

WORKDIR /app

# Install build essentials and create virtual environment in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* && \
    python -m venv /app/venv

# Set virtual environment path
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Copy and install requirements
COPY requirements.txt .
RUN . /app/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy application file
COPY test_app.py .

# Expose port
EXPOSE 8080

# Run streamlit
CMD ["streamlit", "run", "test_app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true", "--server.runOnSave=false"] 