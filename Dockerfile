# Start from a recent release of the 14.04 ubuntu distribution
FROM ubuntu:14.04.5

MAINTAINER Mark Koni Wright <mhwright@stanford.edu>
LABEL version="0.01"

# Update base distribution and install needed packages
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y gcc pkg-config python python-all python-pip python-all-dev libgsl0-dev hdf5-tools hdf5-helpers python-setuptools libhdf5-serial-dev perl perl-modules awscli s3cmd openssh-server openssh-client gnupg time

RUN pip install msprime

ARG UID=1000
RUN useradd --non-unique -u $UID --home /home/popsim --user-group --create-home --shell /bin/bash popsim
ADD . /home/popsim

RUN mkdir -p /home/popsim/shared

RUN chown -R popsim:popsim /home/popsim

USER popsim
RUN mspms 10 1 -t 10 -r 100 1000
WORKDIR /home/popsim
ENTRYPOINT ["/home/popsim/start.sh"]
