FROM dockerfile/python

MAINTAINER <stephane.rault@radicalspam.org>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -q && apt-get install --no-install-recommends -yq \
 python-gevent \
 python-pip

RUN mkdir -p /code
ADD . /code
WORKDIR /code
RUN pip install --force-reinstall -e ./

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD /bin/bash