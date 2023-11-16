FROM python:3.7

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY . .

ENV MAX_CONCURRENT_PIP=4

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
