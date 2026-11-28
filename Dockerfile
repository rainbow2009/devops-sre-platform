FROM python:3.12-slim-bookworm

# Update Debian packages with known security fixes
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpam-modules \
        libpam-modules-bin \
        libpam-runtime \
        libpam0g \
        libzstd1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN groupadd --system app && \
    useradd --system --gid app app

COPY --chown=app:app app/ ./app/

USER app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
