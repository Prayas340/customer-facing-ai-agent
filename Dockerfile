FROM python:3.11-slim

# Set environment variables for Python and Streamlit
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Set working directory
WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default Cloud Run port
EXPOSE 8080

# Run Streamlit on port 8080 and bind to 0.0.0.0
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
