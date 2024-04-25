FROM python:3.11.8

ENV PYTHONUNBUFFERED=1
WORKDIR /JSON_RPC

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./Source/. ./
