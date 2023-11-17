FROM python:3.8

RUN mkdir /usr/app
WORKDIR /usr/app

RUN apt-get update && apt-get install -y cron 

RUN echo '*/15 06-23 * * * printenv > /etc/environment; /usr/bin/python /usr/app/src/scrapers/scraper.py > /usr/app/src/scrapers/scraper.log 2>&1' | crontab -


COPY . .
EXPOSE 5000

RUN pip install -r requirements.txt
