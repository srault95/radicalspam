FROM ubuntu:16.04

ENV ANSIBLE_PLAYBOOK ${ANSIBLE_PLAYBOOK:-radicalspam.yml}

RUN echo "deb http://ppa.launchpad.net/ansible/ansible-1.9/ubuntu xenial main" | tee /etc/apt/sources.list.d/ansible.list \
    && echo "deb-src http://ppa.launchpad.net/ansible/ansible-1.9/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/ansible.list \
    && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7BB9C367 \
    && DEBIAN_FRONTEND=noninteractive apt-get update  \
    && apt-get install -y ansible openssl ca-certificates \
    && echo 'localhost' > /etc/ansible/hosts \
    && touch /var/log/empty.log

WORKDIR /tmp

COPY . /tmp

RUN ansible-playbook ${ANSIBLE_PLAYBOOK} --connection=local

RUN apt-get clean \
	&& rm -rf /etc/apt/sources.list.d/ansible.list /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 25/tcp 465/tcp

CMD ["tail", "-f", "/var/log/empty.log"]
