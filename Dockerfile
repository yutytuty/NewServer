# syntax=docker/dockerfile:1

FROM docker.io/ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip mesa-utils libegl1 build-essential libssl-dev capnproto git
RUN python3 -m pip install -U pip setuptools

ENV ARCADE_HEADLESS=true
ENV LIBGL_ALWAYS_SOFTWARE=true

WORKDIR /root
COPY requirements.txt /root
RUN pip3 install -r requirements.txt
COPY . ./

ENV PATH=/root/.local/bin:$PATH

CMD ["python3", "-u", "src/main.py"]
