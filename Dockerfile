FROM python:3.9
ENV TZ="America/New_York"
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
ENV MAX_CONCURRENT_PIP=4
RUN pip3 install --upgrade pip
RUN pip3 install --exists-action w -r requirements.txt
CMD flask --app migrations db upgrade && python3 app.py