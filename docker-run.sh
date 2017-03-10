#!/bin/bash

# thanks to https://github.com/discourse/discourse_docker/blob/master/discourse-setup

RADICALSPAM_VERSION=4.0.0

DOCKER_IMAGE=${DOCKER_IMAGE:-rs/radicalspam}
CT_NAME=${CT_NAME:-radicalspam}

check_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please sudo or log in as root first." 1>&2
    exit 1
  fi
}

check_memory() {
  avail_mem="$(LANG=C free -m | grep '^Mem:' | awk '{print $2}')"
  if [ "$avail_mem" -lt 900 ]; then
    echo "WARNING: RadicalSpam requires 1GB RAM to run. This system does not appear"
    echo "to have sufficient memory."
  fi
}

check_disk() {
  free_disk="$(df /var | tail -n 1 | awk '{print $4}')"
  if [ "$free_disk" -lt 5000 ]; then
    echo "WARNING: RadicalSpam requires at least 5GB free disk space. This system"
    echo "does not appear to have sufficient disk space."
  fi
}

check_port() {
  local valid=$(netstat -tln | awk '{print $4}' | grep ":${1}\$")
  if [ -n "$valid" ]; then
    echo "ERROR: Port ${1} appears to already be in use."
    exit 1
  fi
}      

check_root
check_memory
check_disk
check_port "25"
check_port "465"
#check_port "8080"

docker kill ${CT_NAME}
docker rm -v ${CT_NAME}
docker rmi -f ${DOCKER_IMAGE}:${RADICALSPAM_VERSION}
docker rmi -f ${DOCKER_IMAGE}

docker build --pull --force-rm --no-cache -t ${DOCKER_IMAGE}:${RADICALSPAM_VERSION} . || exit 1

docker tag ${DOCKER_IMAGE}:${RADICALSPAM_VERSION} ${DOCKER_IMAGE}:latest || exit 1

docker run -d \
   --name ${CT_NAME} \
   --privileged \
   --net host --pid=host \
   -v /etc/localtime:/etc/localtime \
   ${DOCKER_IMAGE}

#docker run -d \
#   --name ${CT_NAME} \
#   --privileged \
#   --net host --pid=host \
#   -v /etc/localtime:/etc/localtime \
#   -v $PWD/store/log:/var/log \
#   -v $PWD/store/amavis/config:/var/lib/amavis/config \
#   -v $PWD/store/amavis/virusmails:/var/lib/amavis/virusmails \
#   -v $PWD/store/postfix/local:/etc/postfix/local \
#   -v $PWD/store/postfix/ssl:/etc/postfix/ssl \
#   -v $PWD/store/postfix/spool:/var/spool/postfix \
#   -v $PWD/store/etc/postgrey/etc:/etc/postgrey \
#   -v $PWD/store/etc/postgrey/data:/var/lib/postgrey \
#   -v $PWD/store/clamav:/var/lib/clamav \
#   -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
#   ${DOCKER_IMAGE}

RET=$?   

docker ps

exit $RET