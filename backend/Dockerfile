FROM python:3.9-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make scripts executable
RUN chmod +x prestart.sh
RUN chmod +x build.sh 2>/dev/null || true

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create necessary directories
RUN mkdir -p cache logs

# Expose the port
EXPOSE 8000

# Run the prestart script and then start the application
CMD ["bash", "-c", "./prestart.sh && uvicorn main:app --host 0.0.0.0 --port $PORT"] 