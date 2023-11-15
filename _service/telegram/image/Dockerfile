ARG PYTHON_ALPINE_IMAGE
FROM $PYTHON_ALPINE_IMAGE

WORKDIR /app

COPY _common/notification/requirements.txt notification/
RUN pip install -r notification/requirements.txt

COPY _common/notification/*.py notification/

COPY _service/telegram/image/requirements.txt ./
RUN pip install -r requirements.txt

COPY _service/telegram/image/*.py ./

ENTRYPOINT [ "python" ]
