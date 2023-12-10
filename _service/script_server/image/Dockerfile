ARG SCRIPT_SERVER_IMAGE
ARG PYTHON_ALPINE_IMAGE

FROM $SCRIPT_SERVER_IMAGE AS script-server

FROM $PYTHON_ALPINE_IMAGE

WORKDIR /app

COPY --from=script-server /app/ /app/
RUN pip install -r requirements.txt

RUN apk add --update --no-cache \
  docker-cli-compose

ENTRYPOINT [ "python", "launcher.py" ]
