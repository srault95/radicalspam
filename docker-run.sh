#!/bin/bash

# thanks to https://github.com/discourse/discourse_docker/blob/master/discourse-setup

DOCKER_IMAGE=${DOCKER_IMAGE:-rs/radicalspam:4.0.0}
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
check_port "8080"
        
#docker build -t rs/base-image:xenial https://github.com/srault95/baseimage-docker.git#base-ubuntu-xenial:image

#docker inspect rs/base-image:xenial 2>/dev/null 1>&2
#if [ "$?" != "0" ]; then
#	echo "The base image for radicalspam is not ready. Error[$?]"
#	exit 1
#fi   

#docker rmi -f ${DOCKER_IMAGE}
#docker rm -v ${CT_NAME}

docker build -t ${DOCKER_IMAGE} .

docker run -d \
   --net host --name ${CT_NAME} \
   --pid=host \
   --env-file=./docker_environ \
   -v /etc/localtime:/etc/localtime \
   -v $PWD/store/amavis:/var/lib/amavis \
   -v $PWD/store/clamav:/var/lib/clamav \
   -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
   -v $PWD/store/postfix/config:/etc/postfix/local \
   -v $PWD/store/postfix/spool:/var/spool/postfix \
   -v $PWD/store/redis/data:/var/lib/redis \
   -v $PWD/store/postgrey/db:/var/lib/postgrey \
   -v $PWD/store/mongodb/data:/var/lib/mongodb \
   ${DOCKER_IMAGE}

RET=$?   

docker ps

exit $RET