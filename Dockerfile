FROM williamyeh/ansible:master-ubuntu16.04-onbuild

ARG POSTGREY_ENABLE
ARG AMAVIS_ENABLE
ARG CLAMAV_ENABLE
ARG SA_ENABLE
ARG POSTFIX_FILTER_ENABLE

ENV POSTGREY_ENABLE ${POSTGREY_ENABLE:-true}
ENV AMAVIS_ENABLE ${AMAVIS_ENABLE:-true}
ENV CLAMAV_ENABLE ${CLAMAV_ENABLE:-true}
ENV SA_ENABLE ${SA_ENABLE:-true}
ENV POSTFIX_FILTER_ENABLE ${POSTFIX_FILTER_ENABLE:-true}

# https://github.com/ansible/ansible/blob/devel/lib/ansible/constants.py
ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_BECOME false
ENV ANSIBLE_DEBUG false
ENV ANSIBLE_TIMEOUT 10

ENV REQUIREMENTS	requirements.yml
ENV PLAYBOOK		radicalspam.yml
ENV INVENTORY		inventory.ini

#VOLUME /var/log \
# /var/lib/amavis/config \
# /var/lib/amavis/virusmails \
# /etc/postfix/local \
# /etc/postfix/ssl \
# /var/spool/postfix \
# /etc/postgrey \
# /var/lib/postgrey \
# /var/lib/clamav \
# /var/lib/users/spamassassin

#ansible-playbook --connection=local --extra-vars "remote_user=root hosts=localhost" -i inventory.ini -l localhost radicalspam.yml
RUN ansible-playbook-wrapper --extra-vars "rs_remote_user=root rs_hosts=localhost"

EXPOSE 25/tcp 465/tcp 9001/tcp

CMD ["/usr/local/bin/supervisor-start"]

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*