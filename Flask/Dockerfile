FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# This ensures that Python output is sent straight to the container log
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "run.py"]
