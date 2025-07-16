FROM python:3.12-slim

RUN apt-get update && apt-get install -y zip
WORKDIR /app

RUN mkdir /opt/python
RUN pip install Pillow -t /opt/python/

CMD ["sleep", "infinity"]