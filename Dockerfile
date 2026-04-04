FROM python:3.10-slim

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:1.0.0 /lambda-adapter /opt/extensions/lambda-adapter

ENV PYTHONUNBUFFERED=1

ARG REQUIREMENTS_FILE=prod.txt

COPY ./requirements /requirements

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r /requirements/${REQUIREMENTS_FILE}

COPY ./app /app
WORKDIR /app

RUN useradd -m user
USER user

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "8", "--timeout", "0", "app.wsgi:application"]