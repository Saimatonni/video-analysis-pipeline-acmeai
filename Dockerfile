FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY synthetic_field_prototype.py .
COPY synthetic_generator.py .

CMD ["python", "synthetic_field_prototype.py"]