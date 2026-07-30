FROM python:3.11-slim
WORKDIR /app
RUN pip install flask requests prometheus-flask-exporter
COPY app.py .
CMD ["python", "app.py"]
