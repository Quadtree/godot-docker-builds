ARG UBUNTU_VERSION=20.04
FROM ubuntu:$UBUNTU_VERSION

RUN echo 'Acquire::http::Pipeline-Depth 0;' >> /etc/apt/apt.conf
RUN DEBIAN_FRONTEND=noninteractive apt-get update
