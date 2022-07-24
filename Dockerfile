FROM python:3.8

ARG project=homecon
ARG version

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

# knxd
RUN mkdir /knxd
WORKDIR /knxd
RUN git clone https://github.com/knxd/knxd.git
WORKDIR /knxd/knxd
RUN git checkout debian

# RUN apt-get install --no-install-recommends build-essential devscripts equivs
# RUN mk-build-deps --install --tool='apt-get --no-install-recommends --yes --allow-unauthenticated' debian/control
# RUN rm -f knxd-build-deps_*.deb
RUN dpkg-buildpackage -b -uc
WORKDIR /knxd
RUN dpkg -i knxd_*.deb knxd-tools_*.deb
WORKDIR /

# homecon
RUN mkdir /homecon
RUN python3 -m venv /homecon/venv
COPY ./dist/homecon-${version}.tar.gz /homecon
RUN /homecon/venv/bin/pip --no-cache-dir install /homecon/homecon-${version}.tar.gz
