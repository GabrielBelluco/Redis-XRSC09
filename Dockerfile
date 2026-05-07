FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Server/ ./Server/

WORKDIR /app/Server

CMD ["python", "/app/Server/calc_worker.py"]
