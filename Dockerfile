FROM python:3.7.9-slim-stretch

WORKDIR /usr/src/app

COPY requirements.txt ./
#RUN apt-get install zbar-tools
#RUN apt-get install gcc

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install zbar
RUN pip install -y pyzbar


COPY . .

CMD [ "python", "./bot.py" ]