FROM williamyeh/ansible:ubuntu16.04-onbuild

# https://github.com/ansible/ansible/blob/devel/lib/ansible/constants.py
ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_BECOME false

ENV REQUIREMENTS	requirements.yml
ENV PLAYBOOK		${PLAYBOOK:-radicalspam.yml}
ENV INVENTORY		inventory.ini
ENV VERBOSE 		${VERBOSE:-}

RUN ansible-playbook-wrapper --extra-vars "remote_user=root hosts=localhost" ${VERBOSE}

EXPOSE 25/tcp 465/tcp

RUN touch /var/log/empty.log

CMD ["tail", "-f", "/var/log/empty.log"]
