FROM python:3.11-slim

WORKDIR /app
RUN pip install flask pyjwt

COPY app.py .

CMD ["python", "app.py"]
