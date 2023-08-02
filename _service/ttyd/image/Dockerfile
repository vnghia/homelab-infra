FROM tsl0922/ttyd:1.7.3-alpine

RUN apk add --update --no-cache \
  openssh-client \
  docker-cli-compose

COPY _service/ttyd/image/ns /usr/local/bin/ns
RUN chmod +x /usr/local/bin/ns
