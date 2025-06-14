FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

WORKDIR /app/barter

EXPOSE 8000

CMD ["gunicorn", "barter.wsgi:application", "--bind", "0.0.0.0:8000"]
