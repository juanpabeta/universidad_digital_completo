FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.lock ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.lock \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --home-dir /app appuser

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

USER appuser
EXPOSE 8000
CMD ["python", "-m", "app.run"]
