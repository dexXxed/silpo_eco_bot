FROM ubuntu

RUN apt-get update && apt-get install -y software-properties-common build-essential
RUN add-apt-repository ppa:deadsnakes/ppa

ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install tzdata


RUN apt-get update && apt-get install -y python3.7 python3-pip python3.7-dev libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libffi-dev
RUN apt-get install -y git wget gcc python3.7-dev unzip zbar-tools libssl-dev
RUN apt-get install -y zlib1g-dev


RUN python3.7 -m pip install pip
RUN apt-get update && apt-get install -y python3-distutils python3-setuptools
RUN python3.7 -m pip install pip --upgrade pip
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install zbar
RUN pip install -y pyzbar


COPY . .

CMD [ "python", "./bot.py" ]