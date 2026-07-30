FROM python:3.11-slim

WORKDIR /app
RUN pip install flask pyjwt prometheus-flask-exporter

COPY app.py .

CMD ["python", "app.py"]
