#!/bin/bash
#set -e

DEBIAN_FRONTEND=noninteractive
AMAVIS_VERSION=${AMAVIS_VERSION:-2.11.0}

apt-get update && apt-get install -y --no-install-recommends \
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
 rep

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