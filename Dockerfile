FROM python:3.9.22-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip --timeout=60 -i https://mirror-pypi.runflare.com/simple
RUN pip install --no-cache-dir -e . --timeout=60 -i https://mirror-pypi.runflare.com/simple

RUN python pipeline/run.py

EXPOSE 8080

CMD ["python", "web_api/application.py"]