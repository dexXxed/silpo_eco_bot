FROM python:3.7.9-slim-stretch

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install zbar
RUN pip install -y pyzbar
RUN apt-get install zbar-tools


COPY . .

CMD [ "python", "./bot.py" ]