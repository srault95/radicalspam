FROM rs/base-image:xenial

ENV GOSU_VERSION 1.7
ENV AMAVIS_VERSION 2.11.0
ENV MY_HOSTNAME mx.example.net
ENV MY_DOMAIN localhost.net
ENV AMAVIS_MAX_SERVERS 2
ENV REDIS_SERVER 127.0.0.1:6379
ENV RSADMIN_HOST 0.0.0.0:8080
ENV RSADMIN_MONGODB_URL mongodb://localhost/radicalspam
ENV DISABLE_SSH 1

RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN echo "postfix postfix/mailname string mx.example.net" | debconf-set-selections
RUN echo "postfix postfix/root_address string root@example.net" | debconf-set-selections
RUN echo "postfix postfix/mynetworks string 172.17.0.0/24" | debconf-set-selections

RUN rm -f /etc/cron.daily/logrotate
#RUN rm -f /etc/service/sshd/down \
#    && /etc/my_init.d/00_regen_ssh_host_keys.sh
# --enable-insecure-key

COPY install.sh /usr/local/bin/install.sh
RUN ["/bin/bash", "/usr/local/bin/install.sh"]

RUN rm -rf /etc/spamassassin/* /etc/cron.daily/spamassassin \
  && rm -f /etc/clamav-unofficial-sigs.conf \
  && rm -f /etc/syslog-ng/syslog-ng.conf \
  && mkdir -p /var/lib/users/spamassassin \
  && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
  && chmod +x /usr/local/bin/gosu \
  && gosu nobody true

ADD postfix/master-amavis.tmpl /etc/postfix/
ADD spamassassin/etc/* /etc/spamassassin/
ADD spamassassin/cron/spamassassin /etc/cron.daily/spamassassin
ADD amavis/99-radicalspam /etc/amavis/conf.d/
ADD amavis/amavisd.conf /etc/amavis/
ADD clamav/clamd.conf /etc/clamav/
ADD clamav/freshclam.conf /etc/clamav/
ADD clamav/clamav-unofficial-sigs.conf /etc/
ADD redis/redis.conf /etc/redis/
ADD web/gunicorn_conf.py /usr/local/etc/gunicorn_conf
ADD syslog-ng/syslog-ng.conf /etc/syslog-ng/
ADD cron/radicalspam.cron /usr/local/etc

ADD tools /usr/local/tools/
RUN chmod +x /usr/local/tools/*

ADD scripts /scripts/

ADD supervisord.conf /etc/supervisor/
RUN echo "alias ctl='supervisorctl -c /etc/supervisor/supervisord.conf'" >> /root/.bashrc \
    && mkdir -p /var/log/supervisor
    && mkdir /etc/service/supervisor \
    && ln -sf /scripts/supervisor.sh /etc/service/supervisor/run 

ADD web /code/
WORKDIR /code/
RUN pip install -r requirements/default.txt \
    && pip install https://github.com/benoitc/gunicorn/tarball/master \
    && pip install --no-deps .

WORKDIR /var/log

#CMD ["/sbin/my_init", "--skip-runit", "runsv", "/etc/service/start"]

RUN apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /code /usr/local/bin/install.sh 

	