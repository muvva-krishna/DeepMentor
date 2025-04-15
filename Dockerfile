# Use a lightweight Python base image
FROM python:3.10-slim

# Set environment variables to avoid prompts during installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including LaTeX and FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    texlive-full \
    manim \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your app files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port Streamlit runs on
EXPOSE 8501

# Set Streamlit environment variable to allow custom ports
ENV STREAMLIT_SERVER_PORT=8501

# Run Streamlit app
CMD ["streamlit", "run", "app.py"]
