FROM python:3.12-alpine

RUN apk add --no-cache libmagic

ENV CONNECTOR_HOME=/opt/opencti-connector-opensourcemalware

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY src ${CONNECTOR_HOME}/src
WORKDIR ${CONNECTOR_HOME}/src

CMD ["python", "connector.py"]
