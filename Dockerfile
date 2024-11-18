FROM python:3.9
ENV TZ="America/New_York"
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
ENV MAX_CONCURRENT_PIP=4
RUN pip3 install --upgrade pip
RUN pip3 install --exists-action w -r requirements.txt

# to receive build arguments
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_NAME
ARG DB_USERNAME
ARG DB_PORT
ARG FLASK_ENV

# set env variables for build
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV DB_NAME=${DB_NAME}
ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PORT=${DB_PORT}
ENV FLASK_ENV=${FLASK_ENV}

RUN flask db upgrade
CMD python3 app.py
