FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-t", "120", "app:app"]
