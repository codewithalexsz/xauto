# Twitter Automation Docker Image
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    gnupg \
    curl \
    unzip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python3 -m venv venv \
    && . venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p app/state chrome-data logs

# Set permissions
RUN chmod +x cli_version.py \
    && chmod +x install.sh \
    && chmod +x run_cli.sh

# Create a non-root user
RUN useradd -m -s /bin/bash twitterbot \
    && chown -R twitterbot:twitterbot /app

# Switch to non-root user
USER twitterbot

# Set the default command
ENTRYPOINT ["./run_cli.sh"]
CMD ["--help"]
