FROM python:3.13-alpine AS builder

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
    postgresql-dev \
    gcc \
    musl-dev \
    libffi-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/* && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -name '__pycache__' -exec rm -rf {} + && \
    rm -rf /root/.cache/pip

FROM python:3.13-alpine AS base

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

RUN adduser -D -u 1000 fastapi-user
ENV PYTHONPATH=/app/

USER fastapi-user