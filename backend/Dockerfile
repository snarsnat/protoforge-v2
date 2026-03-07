FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy source
COPY src/ ./src/

# Create data directory
RUN mkdir -p data/threads

# Expose ports
EXPOSE 8001 2024

# Run gateway
CMD ["python", "-m", "src.gateway.app"]
