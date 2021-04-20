FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update; apt-get -y upgrade
RUN apt-get install -y build-essential \ 
                       libraw-dev \
                       pkg-config
RUN apt-get install -y wget python python-pip python-dev

RUN wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
RUN chmod +x ./Anaconda2-4.2.0-Linux-x86_64.sh
RUN bash ./Anaconda2-4.2.0-Linux-x86_64.sh -b

RUN mkdir /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app

RUN echo 'alias python=/root/anaconda2/bin/python' >> ~/.bashrc
RUN /root/anaconda2/bin/python -m pip install -r requirements.txt

CMD [ "/bin/bash" ]