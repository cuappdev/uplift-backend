FROM python:3.9
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
ENV MAX_CONCURRENT_PIP=4
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD python3 app.py