FROM williamyeh/ansible:ubuntu16.04-onbuild

# https://github.com/ansible/ansible/blob/devel/lib/ansible/constants.py
ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_BECOME false
ENV ANSIBLE_DEBUG false
ENV ANSIBLE_TIMEOUT 10

ENV REQUIREMENTS	requirements.yml
ENV PLAYBOOK		radicalspam.yml
ENV INVENTORY		inventory.ini

RUN ansible-playbook-wrapper --extra-vars "remote_user=root hosts=localhost"

EXPOSE 25/tcp 465/tcp 9001/tcp

VOLUME [
 '/var/log', 
 '/var/lib/amavis/config',
 '/var/lib/amavis/virusmails',
 '/etc/postfix/local',
 '/etc/postfix/ssl',
 '/var/spool/postfix',
 '/etc/postgrey',
 '/var/lib/postgrey',
 '/var/lib/clamav',
 '/var/lib/users/spamassassin']

CMD ["/usr/local/bin/supervisor-start"]
