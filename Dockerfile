FROM python:3.12-alpine

RUN apk update && apk add --no-cache \
    chromium \
    chromium-chromedriver

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
