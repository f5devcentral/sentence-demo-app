FROM python:3.10-alpine

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /
COPY config.py /

WORKDIR /

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:8080", "app:generator"]