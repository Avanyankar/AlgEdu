FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DB_PATH=/app/db.sqlite3 \
    STATIC_ROOT=/app/staticfiles

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn AlgEdu_Team.wsgi:application --bind 0.0.0.0:8000"]