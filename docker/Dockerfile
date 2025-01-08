FROM python:3.12-slim

# Set the working directory
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD python3 run.py
