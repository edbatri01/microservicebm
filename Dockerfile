FROM python:3

WORKDIR /myapp

COPY requirements.txt .

RUN  pip install --no-cache-dir -r requirements.txt
COPY app.py .

CMD ["python3", "app.py"]