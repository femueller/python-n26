# Docker image for n26

# dont use alpine for python builds: https://pythonspeed.com/articles/alpine-docker-python/
FROM python:3.9-slim-buster

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get -y install sudo python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip;\
    pip install pipenv;\
    PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy;\
    pip install .

ENTRYPOINT [ "n26" ]
CMD [ "-h" ]