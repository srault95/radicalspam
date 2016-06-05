FROM rs/base-image:xenial

ENV GOSU_VERSION 1.7
ENV AMAVIS_VERSION 2.11.0
ENV MY_HOSTNAME mx.example.net
ENV MY_DOMAIN localhost.net
ENV AMAVIS_MAX_SERVERS 2
ENV REDIS_SERVER 127.0.0.1:6379
ENV RSADMIN_HOST 0.0.0.0:8080
ENV RSADMIN_MONGODB_URL mongodb://localhost/radicalspam

RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN echo "postfix postfix/mailname string mx.example.net" | debconf-set-selections
RUN echo "postfix postfix/root_address string root@example.net" | debconf-set-selections
RUN echo "postfix postfix/mynetworks string 172.17.0.0/24" | debconf-set-selections

RUN rm -f /etc/cron.daily/logrotate

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

ADD scripts/freshclam.sh /etc/service/freshclam/run
ADD scripts/clamd.sh /etc/service/clamd/run
ADD scripts/spamd.sh /etc/service/spamd/run
ADD scripts/amavis.sh /etc/service/amavis/run
ADD scripts/postfix.sh /etc/service/postfix/run
ADD scripts/redis.sh /etc/service/redis/run
ADD scripts/postgrey.sh /etc/service/postgrey/run
ADD scripts/rs-admin.sh /etc/service/rs-admin/run
ADD scripts/mongodb.sh /etc/service/mongodb/run

ADD tools /usr/local/tools/
ADD cron/radicalspam.cron /usr/local/etc

RUN chmod +x /etc/service/freshclam/run \
	/etc/service/clamd/run \
	/etc/service/spamd/run \
	/etc/service/amavis/run \
	/etc/service/postfix/run \
	/etc/service/redis/run \
	/etc/service/postgrey/run \
	/etc/service/rs-admin/run \
	/usr/local/tools/* \
	/etc/service/mongodb/run

ADD web /code/
WORKDIR /code/
RUN pip install -r requirements/default.txt \
    && pip install https://github.com/benoitc/gunicorn/tarball/master \
    && pip install --no-deps .

WORKDIR /var/log

CMD ["/sbin/my_init"]

RUN apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /code /usr/local/bin/install.sh 
