#!/bin/bash

CLEANUP_QUARANTINE="${CLEANUP_QUARANTINE:-no}"

if [ "${CLEANUP_QUARANTINE}" != "yes" ];
	exit 0
fi

BASEDIR=/var/lib/amavis/quarantine

#TODO: archives

if [ -d ${BASEDIR}/virus -a "${CLEANUP_QUARANTINE_VIRUS}" != "0" ]; then
	find ${BASEDIR}/virus -type f -mtime +${CLEANUP_QUARANTINE_VIRUS} -exec rm -f {} \;
fi

if [ -d ${BASEDIR}/banned -a "${CLEANUP_QUARANTINE_BANNED}" != "0" ]; then
	find ${BASEDIR}/banned -type f -mtime +${CLEANUP_QUARANTINE_BANNED} -exec rm -f {} \;
fi

if [ -d ${BASEDIR}/spam -a "${CLEANUP_QUARANTINE_SPAM}" != "0" ]; then
	find ${BASEDIR}/spam -type f -mtime +${CLEANUP_QUARANTINE_SPAM} -exec rm -f {} \;
fi

