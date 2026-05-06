FROM python:3.12-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=120 --retries 10 -r requirements.txt


COPY . .
