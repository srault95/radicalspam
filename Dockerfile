FROM williamyeh/ansible:ubuntu16.04-onbuild

# https://github.com/ansible/ansible/blob/devel/lib/ansible/constants.py
ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_BECOME false
ENV ANSIBLE_DEBUG false
ENV ANSIBLE_TIMEOUT 10

ENV REQUIREMENTS	requirements.yml
ENV PLAYBOOK		${PLAYBOOK:-radicalspam.yml}
ENV INVENTORY		inventory.ini
ENV VERBOSE 		${VERBOSE:-} #-vvvv

RUN ansible-playbook-wrapper --extra-vars "remote_user=root hosts=localhost" ${VERBOSE}

EXPOSE 25/tcp 465/tcp

RUN touch /var/log/empty.log

CMD ["/usr/bin/radicalspam-start"]
