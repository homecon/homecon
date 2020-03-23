FROM python:3.6

ARG project=homecon


ENV TERM=xterm \
    TZ=Europe/Brussels \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
       build-essential \
       git-core \
       coinor-cbc \
       gfortran \
       glpk-utils \
       libatlas-base-dev \
       libblas-dev \
       libcairo2 \
       libffi6 \
       libffi-dev \
       liblapack-dev \
       make \
       python3-tk \
       python3-pip \
       python3-dev \
       python3-setuptools \
       debhelper\
       libusb-1.0-0-dev \
       libsystemd-dev \
       libev-dev \
       libfmt-dev \
   && rm -rf /var/lib/apt/lists/*


# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /homecon

COPY ./requirements.txt /homecon

# RUN pip3 --no-cache-dir install -U pip wheel setuptools
RUN pip3 --no-cache-dir install -r /homecon/requirements.txt

COPY ./homecon       /homecon/homecon
COPY ./app/build     /homecon/app/build

ENV PYTHONPATH /homecon


# knxd
RUN git clone https://github.com/knxd/knxd.git
WORKDIR /knxd
RUN dpkg-buildpackage -b -uc
WORKDIR /
RUN dpkg -i knxd_*.deb knxd-tools_*.deb
