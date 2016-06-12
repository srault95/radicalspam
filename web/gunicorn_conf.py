# -*- coding: utf-8 -*-

try:
    import multiprocessing
    CPU_COUNT = (multiprocessing.cpu_count() * 2) +1
except:
    CPU_COUNT = 1

from decouple import config as env_config

bind = env_config('RSADMIN_HOST', '0.0.0.0:8080')

daemon = False

#chdir = "/code"

preload = env_config('RSADMIN_PRELOAD', False, cast=bool)

proxy_protocol = env_config('RSADMIN_PROXY_PROTOCOL', True, cast=bool)

proxy_allow_ips = env_config('RSADMIN_PROXY_ALLOW_IPS', "127.0.0.1")

forwarded_allow_ips = env_config('RSADMIN_FORWARDED_ALLOW_IPS', "*")

workers = env_config('RSADMIN_WORKERS', CPU_COUNT, cast=int)

worker_class = env_config('RSADMIN_WORKER_CLASS', 'gevent_wsgi')

worker_connections = env_config('RSADMIN_WORKER_CONNECTIONS', 200, cast=int)

backlog = env_config('RSADMIN_BACKLOG', 2048, cast=int)

timeout = env_config('RSADMIN_TIMEOUT', 60, cast=int)

keepalive = env_config('RSADMIN_KEEPALIVE', 2, cast=int)

debug = env_config('RSADMIN_DEBUG', False, cast=bool)

#TODO: logger_class
loglevel = env_config('RSADMIN_LOG_LEVEL', 'info')

accesslog = env_config('RSADMIN_ACCESSLOG', "-")

errorlog = env_config('RSADMIN_ERRORLOG', "-")

syslog = env_config('RSADMIN_SYSLOG', False, cast=bool)

#TODO: limit_request_line=4094
#TODO: limit_request_fields=100
#TODO: limit_request_field_size=8190
#TODO: tmp_upload_dir

if syslog:
    #use --link=syslog:syslog
    #tcp://HOST:PORT
    syslog_addr = env_config('RSADMIN_SYSLOG_ADDR', 'udp://syslog:514')


logconfig = env_config('RSADMIN_LOGCONFIG', None)

statsd_enable = env_config('RSADMIN_STATSD_ENABLE', False, cast=bool)

if statsd_enable:
    #host:port
    statsd_host = env_config('RSADMIN_STATSD_HOST', None)
    statsd_prefix = env_config('RSADMIN_STATSD_PREFIX', 'rsadmin')
