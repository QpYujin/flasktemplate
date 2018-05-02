FROM ubuntu:latest

MAINTAINER Mallikarjun

RUN apt-get update -y

RUN apt-get install -y python-pip python-dev build-essential

RUN pip install flask-api

RUN pip install psutil

RUN pip install Flask-MySQLdb

WORKDIR /home/ubuntu/flaskserver

COPY . /home/ubuntu/flaskserver

RUN pip install -r requirements.txt

EXPOSE 8000
EXPOSE 5000

CMD ["python","app.py"]
