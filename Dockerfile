# Build stage - includes GCC, g++, and git for compiling dependencies
FROM python:3.12 AS builder

# Set the working directory inside the container
WORKDIR /app

# Install build dependencies (GCC, g++, git, etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Run stage - minimal runtime image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy the application code into the container
COPY . .

# Create audio directory with full permissions
RUN mkdir -p /app/audiofiles && chmod 777 /app/audiofiles

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set audio upload directory
ENV AUDIO_UPLOAD_DIR=/app/audiofiles

# Expose the port that the application will listen on
EXPOSE 8080

ENV PYTHONUNBUFFERED=TRUE

# Command to run the application
CMD python app.py
