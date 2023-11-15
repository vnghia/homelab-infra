ARG PYTHON_ALPINE_IMAGE
ARG RESTIC_IMAGE

FROM $RESTIC_IMAGE as restic

FROM $PYTHON_ALPINE_IMAGE

WORKDIR /app

RUN apk add --update --no-cache \
  docker-cli-compose

COPY --from=restic /usr/bin/restic /usr/bin/restic

COPY _common/notification/requirements.txt notification/
RUN pip install -r notification/requirements.txt

COPY _common/notification/*.py notification/

COPY _data/backup/image/requirements.txt ./
RUN pip install -r requirements.txt

COPY _data/backup/image/*.py ./

ENTRYPOINT [ "python", "main.py" ]
