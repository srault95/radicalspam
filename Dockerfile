FROM williamyeh/ansible:ubuntu16.04-onbuild

ENV PLAYBOOK ${PLAYBOOK:-radicalspam.yml}

RUN ansible-playbook-wrapper --extra-vars "remote_user=root"

EXPOSE 25/tcp 465/tcp

RUN touch /var/log/empty.log

CMD ["tail", "-f", "/var/log/empty.log"]
