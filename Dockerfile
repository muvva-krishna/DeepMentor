FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"

# Install system dependencies including FFmpeg, LaTeX, and others
RUN apt-get update && apt-get install -y \
    ffmpeg \
    texlive-latex-base \
    git \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install manim

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
