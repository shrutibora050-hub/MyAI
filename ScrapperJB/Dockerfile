# Using Alpine Linux for minimal size (~5MB base vs ~130MB for standard Python)
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install git (needed for Simplify scraper to pull repo)
# Alpine uses apk package manager - very lightweight
RUN apk add --no-cache git

# Copy only requirements first (Docker layer caching - won't reinstall if requirements unchanged)
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir prevents pip from storing cache, saves space
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scraper/ ./scraper/
COPY main.py .
COPY graphql_server.py .

# Clone Simplify repository
RUN git clone --depth 1 https://github.com/SimplifyJobs/New-Grad-Positions.git simplify_data

# Create output directory
RUN mkdir -p output

# Expose GraphQL port
EXPOSE 8000

# Default command - run GraphQL server
CMD ["python", "graphql_server.py"]
