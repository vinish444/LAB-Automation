FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/docker/api-start.sh /app/docker/celery-start.sh

ENV PYTHONPATH=/app
ENV NET_TEXTFSM=/app/templates/textfsm/ntc_templates/templates

EXPOSE 8000
