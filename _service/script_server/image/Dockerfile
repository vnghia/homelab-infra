FROM python:3.11.4-alpine3.18

WORKDIR /app

RUN apk add --update --no-cache \
  docker-cli-compose

RUN wget https://github.com/bugy/script-server/releases/download/1.18.0/script-server.zip -O /tmp/app.zip \
  && unzip /tmp/app.zip -d /app \
  && rm -rf /tmp/app.zip
RUN pip install -r requirements.txt

CMD [ "python", "launcher.py" ]
