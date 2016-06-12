#!/bin/bash

set -e

DEBIAN_FRONTEND=noninteractive
AMAVIS_VERSION=${AMAVIS_VERSION:-2.11.0}

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927

echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.2.list

apt-get update && apt-get install -y --no-install-recommends \
 build-essential \
 python3-dev \
 python3-setuptools \
 ca-certificates \
 curl \
 wget \
 xz-utils \
 p0f \
 pax \
 arj \
 bzip2 \
 cabextract \
 cpio \
 lhasa \
 lzop \
 nomarch \
 p7zip \
 unrar-free \
 libnet-patricia-perl \
 ripole \
 libzeromq-perl \
 opendkim \
 spamassassin \
 spamc \
 sa-compile \
 spamassassin-rules-ja \
 gnupg \
 razor \
 pyzor \
 clamav \
 clamav-daemon \
 clamdscan \
 clamav-unofficial-sigs \
 amavisd-new \
 postgrey \
 postfix \
 redis-server \
 rep \
 syslog-ng-mod-mongodb \
 mongodb-org
 
#TODO: mongodb-org mongodb-org-mongos mongodb-org-server mongodb-org-shell mongodb-org-tools 

curl -k https://bootstrap.pypa.io/get-pip.py | python3 -

wget http://www.ijs.si/software/amavisd/amavisd-new-${AMAVIS_VERSION}.tar.xz \
  && tar -Jxvf amavisd-new-${AMAVIS_VERSION}.tar.xz \
  && rm -f amavisd-new-${AMAVIS_VERSION}.tar.xz \
  && cp -v amavisd-new-${AMAVIS_VERSION}/amavisd /usr/local/bin/amavisd-new \
  && find amavisd-new-${AMAVIS_VERSION} -type f -name "amavisd-*" -executable -exec cp -va {} test \; \
  && rm -rf amavisd-new-${AMAVIS_VERSION} || exit 1
  
adduser clamav amavis
adduser amavis clamav
adduser debian-spamd amavis
adduser amavis debian-spamd

ln -sf /usr/local/etc/radicalspam.cron /etc/cron.d/radicalspam