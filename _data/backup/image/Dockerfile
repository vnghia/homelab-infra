FROM python:3.11.4

WORKDIR /app

COPY --from=restic/restic:0.16.0 /usr/bin/restic /usr/bin/restic

COPY _common/notification/requirements.txt notification/
RUN pip install -r notification/requirements.txt

COPY _common/notification/*.py notification/

COPY _data/backup/image/requirements.txt ./
RUN pip install -r requirements.txt

COPY _data/backup/image/*.py ./

ENTRYPOINT [ "python", "main.py" ]
