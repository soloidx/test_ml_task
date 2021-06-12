FROM python:3.9-alpine

WORKDIR /rq_worker

RUN pip install rq

COPY settings.py ./

ENTRYPOINT ["rq", "worker", "-c","settings"]
