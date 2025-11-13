# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies step by step
RUN pip install --no-cache-dir fastapi==0.104.1 pydantic==2.5.0 python-dotenv==1.0.0
RUN pip install --no-cache-dir pytest==7.4.3 httpx==0.25.2
RUN pip install --no-cache-dir uvicorn[standard]==0.24.0 python-multipart==0.0.6
RUN pip install --no-cache-dir edison-client==0.7.6

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
