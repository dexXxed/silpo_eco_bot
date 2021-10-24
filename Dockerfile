FROM ubuntu

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN apt-get install -y git wget gcc python3.7-dev unzip

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