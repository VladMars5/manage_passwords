FROM python:3.10

RUN mkdir /app
WORKDIR /app

RUN apt-get update
RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker/*.sh