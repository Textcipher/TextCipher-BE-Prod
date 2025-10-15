FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y pkg-config libmariadb-dev vim

RUN python3 -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

COPY . /app/

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["gunicorn", "TextCipher.wsgi:application", "--bind", "0.0.0.0:8002"]