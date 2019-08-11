FROM python:3.7.4-buster

RUN pip install flask>=0.13.2 \
    pytest>=3.10.0 \
    gunicorn==19.9.0 \
    loguru>=0.2.4 \
    pymongo>=3.7.2

COPY . /app
WORKDIR /app

