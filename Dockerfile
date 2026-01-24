FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
# FIX: Added 'zstd' to the list of packages
RUN apt-get update && apt-get install -y \
    curl \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code and entrypoint
COPY src/ src/
COPY tests/ tests/
COPY entrypoint.sh .

# Make script executable
RUN chmod +x entrypoint.sh

# Set Python path
ENV PYTHONPATH=/app

# Start via the shell script
ENTRYPOINT ["./entrypoint.sh"]
