FROM python:3.11.4

WORKDIR /app

COPY --from=restic/restic:0.16.0 /usr/bin/restic /usr/bin/restic

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY _file.py _file.py
COPY main.py main.py

ENTRYPOINT [ "python", "main.py" ]
