# syntax=docker/dockerfile:1

FROM docker.io/python:3.11-slim-buster AS updated-python

ENV PATH=/root/.local/bin:$PATH
RUN apt-get update && \
    python3 -m pip install -U pip setuptools

FROM updated-python AS builder

WORKDIR /usr/src/ColossalCyberServerAdventure

ENV FLIT_ROOT_INSTALL=1

# Install build dependencies
RUN apt-get install -y --no-install-recommends build-essential libssl-dev capnproto git freeglut3-dev libosmesa6-dev mesa-utils && \
    pip3 install --user flit

# Installing the dependencies and the package itself in seperate stages helps
# Docker cache the dependencies and reduce build time
COPY pyproject.toml .
RUN mkdir -p src/cca_server
COPY src/cca_server/__init__.py src/cca_server/main.py src
RUN flit install --only-deps --user

COPY . .
RUN flit install --user

FROM updated-python

ENV ARCADE_HEADLESS=true LIBGL_ALWAYS_SOFTWARE=true

RUN apt-get install -y --no-install-recommends mesa-utils libegl1 libfreetype6

COPY --from=builder /root/.local /root/.local

CMD ["cca-server"]
