FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# This ensures that Python output is sent straight to the container log
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "run.py"]
