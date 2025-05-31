# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install git in case some packages need it
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . /app

# Ensure credentials directory exists
RUN mkdir -p /app/google_sheet

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Optional: expose Flask if you're running a Flask server (e.g. timeline web app)
EXPOSE 5000

# Default command (runs auto scraper and import script)
CMD ["python", "auto_scrape_and_import.py"]
