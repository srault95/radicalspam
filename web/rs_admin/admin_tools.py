

"""
- liste des services

- psutils
"""

"""
>>> import envoy
>>> r = envoy.run('/usr/bin/sv status /etc/service/clamd')
>>> print(r.status_code)
0
>>> print(r.std_out)
run: /etc/service/clamd: (pid 19586) 1346s
>>> print(r.std_err)

# un up ou down n'a pas de stdout

# status si ferme:
>>> print(r.std_out)
down: /etc/service/clamd: 16s, normally up
>>> print(r.std_out.split())
['down:', '/etc/service/clamd:', '16s,', 'normally', 'up']

['run:', '/etc/service/clamd:', '(pid', '21350)', '6s']
>>> print(r.std_out.split(':'))
['run', ' /etc/service/clamd', ' (pid 21350) 6s\n']


Avec erreur volontaire:
>>> r = envoy.run('/usr/bin/sv status /etc/service/clamd2')
>>> print(r.status_code)
1
>>> print(r.std_err)

>>> print(r.std_out)
fail: /etc/service/clamd2: unable to change to service directory: file does not exist

root@ns397840:/var/log# more /etc/service/clamd/supervise/pid
21614

root@ns397840:/var/log# more /etc/service/clamd/supervise/stat
run

"""

from collections import OrderedDict
import envoy

SERVICES = [
    "freshclam",
    "cron",
    "spamd",
    #"sshd",
    "clamd",
    "mongodb",
    "amavis",
    "postfix",
    #"syslog-forwarder",
    #"syslog-ng",
    "postgrey",
    "redis",
]

CMD_SV = "/usr/bin/sv"
CMD_SV_STATUS = "%s status" % CMD_SV
CMD_SV_START = "%s up" % CMD_SV
CMD_SV_STOP = "%s down" % CMD_SV
CMD_SV_RELOAD = "%s hup" % CMD_SV

SV_PID = "/etc/service/%s/supervise/pid"
SV_STATUS = "/etc/service/%s/supervise/stat"
#TODO: restart ?

SV_UP = "UP"
SV_DOWN = "DOWN"
SV_ERROR = "ERROR"
SV_UNKNOW = "UNKNOW"

def get_pid(service):
    try:
        with open('/etc/service/%s/supervise/pid' % service, 'r') as fp:
            return int(fp.read().strip())
    except:
        return 1

def get_status(envoy_response, service=None):
    _status = {
        'status_code': envoy_response.status_code,
        'state': None,
        'pid': None,
        'duration': 0,
        'output': envoy_response.std_out,
        'is_error': False
    }
    state = SV_UNKNOW
    
    output = envoy_response.std_out
    if not output:
        output = envoy_response.std_err
        if envoy_response.std_err:
            _status["is_error"] = True
    
    if _status["status_code"] != 0:
        _status["is_error"] = True
        
    if not output:
        state = SV_UNKNOW
    elif output.startswith("run"):
        state = SV_UP
    elif output.startswith("down"):
        state = SV_DOWN
    else:
        state = SV_UNKNOW
    
    _status['state'] = state
    
    if service and _status["state"] in [SV_UP]:
        _status["pid"] = get_pid(service)
    
    return _status

def sv_command(command, service=None):
    r = envoy.run(command)
    return get_status(r, service)

def service_start(service):
    return sv_command('%s /etc/service/%s' % (CMD_SV_START, service), service)

def service_stop(service):
    return sv_command('%s /etc/service/%s' % (CMD_SV_STOP, service), service)

def service_reload(service):
    return sv_command('%s /etc/service/%s' % (CMD_SV_RELOAD, service), service)

def service_status(service=None):
    if service:
        return {
            service: sv_command('%s /etc/service/%s' % (CMD_SV_STATUS, service), service)
        }
    else:
        result = OrderedDict()
        for service in SERVICES:
            result[service] = sv_command('%s /etc/service/%s' % (CMD_SV_STATUS, service), service)
        return result
    

if __name__ == "__main__":
    import sys
    from pprint import pprint
    
    arg = None
    cmd = None
    if "status" in sys.argv:
        cmd = service_status
    elif "start" in sys.argv:
        cmd = service_start
    elif "stop" in sys.argv:
        cmd = service_stop
    
    if len(sys.argv) == 3:
        arg = sys.argv[2]
    
    result = cmd(arg)
    pprint(dict(result))
        
        