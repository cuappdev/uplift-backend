FROM python:3.7

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

COPY . .

ENV MAX_CONCURRENT_PIP=4

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python c2c_scraper.py

CMD gunicorn -w 4 -t 300 --graceful-timeout 60 -b 0.0.0.0:8000 app:app
