# -*- coding: utf-8 -*-

"""
>>> import xmlrpclib
>>> from pprint import pprint as pp
>>> server = xmlrpclib.Server('http://127.0.0.1:9001/RPC2')
>>> server.system.listMethods()
>>> infos = server.supervisor.getAllProcessInfo()
>>> infos[0]
>>> pp(infos[0])
{'description': 'pid 61, uptime 0:01:18',
 'exitstatus': 0,
 'group': 'amavis',
 'logfile': '/var/log/supervisor/amavis.log',
 'name': 'amavis',
 'now': 1422462337,
 'pid': 61,
 'spawnerr': '',
 'start': 1422462259,
 'state': 20,
 'statename': 'RUNNING',
 'stderr_logfile': '/var/log/supervisor/amavis.log',
 'stdout_logfile': '/var/log/supervisor/amavis.log',
 'stop': 0} 
"""

#---ProcessInfo
"""
>>> amavis = server.supervisor.getProcessInfo('amavis')
>>> pp(amavis)
{'description': 'pid 61, uptime 0:29:27',
 'exitstatus': 0,
 'group': 'amavis',
 'logfile': '/var/log/supervisor/amavis.log',
 'name': 'amavis',
 'now': 1422464026,
 'pid': 61,
 'spawnerr': '',
 'start': 1422462259,
 'state': 20,
 'statename': 'RUNNING',
 'stderr_logfile': '/var/log/supervisor/amavis.log',
 'stdout_logfile': '/var/log/supervisor/amavis.log',
 'stop': 0}
"""

#---Methods
"""
['supervisor.addProcessGroup',
 'supervisor.clearAllProcessLogs',
 'supervisor.clearLog',
 'supervisor.clearProcessLog',
 'supervisor.clearProcessLogs',
 'supervisor.getAPIVersion',
 'supervisor.getAllConfigInfo',
 'supervisor.getAllProcessInfo',
 'supervisor.getIdentification',
 'supervisor.getPID',
 'supervisor.getProcessInfo',
 'supervisor.getState',
 'supervisor.getSupervisorVersion',
 'supervisor.getVersion',
 'supervisor.readLog',
 'supervisor.readMainLog',
 'supervisor.readProcessLog',
 'supervisor.readProcessStderrLog',
 'supervisor.readProcessStdoutLog',
 'supervisor.reloadConfig',
 'supervisor.removeProcessGroup',
 'supervisor.restart',
 'supervisor.sendProcessStdin',
 'supervisor.sendRemoteCommEvent',
 'supervisor.shutdown',
 'supervisor.signalAllProcesses',
 'supervisor.signalProcess',
 'supervisor.signalProcessGroup',
 'supervisor.startAllProcesses',
 'supervisor.startProcess',
 'supervisor.startProcessGroup',
 'supervisor.stopAllProcesses',
 'supervisor.stopProcess',
 'supervisor.stopProcessGroup',
 'supervisor.tailProcessLog',
 'supervisor.tailProcessStderrLog',
 'supervisor.tailProcessStdoutLog',
 'system.listMethods',
 'system.methodHelp',
 'system.methodSignature',
 'system.multicall']
"""


import errno
from functools import wraps

"""
try: # pragma: no cover
    from base64 import decodebytes as decodestring, encodebytes as encodestring
except ImportError: # pragma: no cover
    from base64 import decodestring, encodestring
"""
#from six.moves import urllib
#from six.moves import urlparse
#from six.moves import http_client as httplib  
from six.moves import xmlrpc_client as xmlrpclib

import socket
bin_socket = socket.socket
text_socket = bin_socket

from flask import Blueprint, jsonify
from .extensions import auth#, cache

_ = lambda s:s

STATUS_STOPPED = 0
STATUS_EXITED = 100
STATUS_FATAL = 200

STATUS_STARTING = 10
STATUS_RUNNING = 20
STATUS_BACKOFF = 30
STATUS_STOPPING = 40
STATUS_UNKNOWN = 1000

STOPPED_STATES = (STATUS_STOPPED,
                  STATUS_EXITED,
                  STATUS_FATAL,
                  STATUS_UNKNOWN)

RUNNING_STATES = (STATUS_RUNNING,
                  STATUS_BACKOFF,
                  STATUS_STARTING)

SUPERVISOR_STATUS_CHOICES = (
    (STATUS_STOPPED, _(u'The process has been stopped due to a stop request or has never been started.')),
    (STATUS_STARTING, _(u'The process is starting due to a start request.')),
    (STATUS_RUNNING, _(u'The process is running.')),
    (STATUS_BACKOFF, _(u'The process entered the STARTING state but subsequently exited too quickly to move to the RUNNING state.')),
    (STATUS_STOPPING, _(u'The process is stopping due to a stop request.')),
    (STATUS_EXITED, _(u'The process exited from the RUNNING state (expectedly or unexpectedly).')),
    (STATUS_FATAL, _(u'The process could not be started successfully.')),
    (STATUS_UNKNOWN, _(u'The process is in an unknown state (supervisord programming error).')),
)

#Fournit un dict par valeur de status - clé = valeur numérique du status
SUPERVISOR_STATUS_DICT = dict(SUPERVISOR_STATUS_CHOICES)


#def as_string(s): return s if isinstance(s, unicode) else s.decode('utf-8')
#def as_bytes(s): return s if isinstance(s, str) else s.encode('utf-8')

class XMLRPCError(Exception):
    
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def response_api(func):
    """
    A mettre en premier
    
    @utils.response_api
    def myview():
        return dict()    
    """
    RESPONSE = {
        'success': True,
        'error': None,
        'values': None,
    }

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            RESPONSE['success'] = True
            RESPONSE['values'] = result
            return dict(response=RESPONSE)
        except Exception as err:
            RESPONSE['success'] = False
            RESPONSE['error'] = str(err)
            return dict(response=RESPONSE)
            
    return wrapper
       

def xmlrpc_error(func):
    u"""Enveloppe le résultat d'une fonction dans un ProxyResults
    
    Toutes exceptions est capturé et ajouté à l'instance de ProxyResults 
    
    @xmlrpc_error
    def support_ipv6():
        return socket.has_ipv6

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
            """
            result = func(*args, **kwargs)
            greenlet = gevent.spawn(func, *args, **kwargs)
            #TODO: timeout
            gevent.joinall([greenlet])
            if greenlet.successful():
                return greenlet.value
            else:
                print "greenlet.exception : ", greenlet.exception
                raise XMLRPCError(u'Connection refused', status_code=410, payload=dict(error=str(greenlet.exception)))
            """
        except xmlrpclib.Fault as err:
            raise XMLRPCError(str(err), status_code=410, payload=dict(faultCode=err.faultCode, faultString=err.faultString))
        except socket.error as err:
            if err.errno == 10061:
                raise XMLRPCError(u'Connection refused', status_code=410, payload=dict(errno=err.errno))
            else:
                raise XMLRPCError(u'Connection error unknow', status_code=410, payload=dict(errno=err.errno))
            #print "socket error : ", err, type(err), dir(err)
            #print "errno', 'message', 'strerror : ", err.errno, err.message, err.strerror
        except Exception as err:
            import traceback
            traceback.print_exc()
            if isinstance(err, (xmlrpclib.Fault, socket.error)):
                raise
            raise XMLRPCError(u'Server error unknow', status_code=410)

    return wrapper

"""
class SupervisorTransport(xmlrpclib.Transport):
    connection = None

    def __init__(self, username=None, password=None, serverurl=None):
        xmlrpclib.Transport.__init__(self)
        self.username = username
        self.password = password
        self.verbose = False
        self.serverurl = serverurl
        if serverurl.startswith('http://'):
            type, uri = urllib.splittype(serverurl)
            host, path = urllib.splithost(uri)
            host, port = urllib.splitport(host)
            if port is None:
                port = 80
            else:
                port = int(port)
            def get_connection(host=host, port=port):
                return httplib.HTTPConnection(host, port)
            self._get_connection = get_connection
        elif serverurl.startswith('https://'):
            type, uri = urllib.splittype(serverurl)
            host, path = urllib.splithost(uri)
            host, port = urllib.splitport(host)
            if port is None:
                port = 443
            else:
                port = int(port)
            def get_connection(host=host, port=port):
                #print "host / port :", host, port
                return httplib.HTTPSConnection(host, port, strict=False
                                               #key_file, cert_file, strict, timeout, source_address
                                               )
            self._get_connection = get_connection
        elif serverurl.startswith('unix://'):
            def get_connection(serverurl=serverurl):
                # we use 'localhost' here because domain names must be
                # < 64 chars (or we'd use the serverurl filename)
                conn = UnixStreamHTTPConnection('localhost')
                conn.socketfile = serverurl[7:]
                return conn
            self._get_connection = get_connection
        else:
            raise ValueError('Unknown protocol for serverurl %s' % serverurl)

    def request(self, host, handler, request_body, verbose=0):
        if not self.connection:
            self.connection = self._get_connection()
            self.headers = {
                "User-Agent" : self.user_agent,
                "Content-Type" : "text/xml",
                "Accept": "text/xml"
                }

            # basic auth
            if self.username is not None and self.password is not None:
                unencoded = "%s:%s" % (self.username, self.password)
                encoded = as_string(encodestring(as_bytes(unencoded)))
                encoded = encoded.replace('\n', '')
                encoded = encoded.replace('\012', '')
                self.headers["Authorization"] = "Basic %s" % encoded

        self.headers["Content-Length"] = str(len(request_body))

        self.connection.request('POST', handler, request_body, self.headers)

        r = self.connection.getresponse()

        if r.status != 200:
            self.connection.close()
            self.connection = None
            raise xmlrpclib.ProtocolError(host + handler,
                                          r.status,
                                          r.reason,
                                          '' )
        data = r.read()
        p, u = self.getparser()
        p.feed(data)
        p.close()
        return u.close()

class UnixStreamHTTPConnection(httplib.HTTPConnection):
    def connect(self): # pragma: no cover
        self.sock = text_socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # we abuse the host parameter as the socketname
        self.sock.connect(self.socketfile)
"""

"""
>>> server = xmlrpclib.Server('http://localhost:9001/RPC2')
>>> server.supervisor.getState()
{'statename': 'RUNNING', 'statecode': 1}

>>> pp(server.system.listMethods())
['supervisor.addProcessGroup',
 'supervisor.clearAllProcessLogs',
 'supervisor.clearLog',
 'supervisor.clearProcessLog',
 'supervisor.clearProcessLogs',
 'supervisor.getAPIVersion',
 'supervisor.getAllConfigInfo',
 'supervisor.getAllProcessInfo',
 'supervisor.getIdentification',
 'supervisor.getPID',
 'supervisor.getProcessInfo',
 'supervisor.getState',
 'supervisor.getSupervisorVersion',
 'supervisor.getVersion',
 'supervisor.readLog',
 'supervisor.readMainLog',
 'supervisor.readProcessLog',
 'supervisor.readProcessStderrLog',
 'supervisor.readProcessStdoutLog',
 'supervisor.reloadConfig',
 'supervisor.removeProcessGroup',
 'supervisor.restart',
 'supervisor.sendProcessStdin',
 'supervisor.sendRemoteCommEvent',
 'supervisor.shutdown',
 'supervisor.signalAllProcesses',
 'supervisor.signalProcess',
 'supervisor.signalProcessGroup',
 'supervisor.startAllProcesses',
 'supervisor.startProcess',
 'supervisor.startProcessGroup',
 'supervisor.stopAllProcesses',
 'supervisor.stopProcess',
 'supervisor.stopProcessGroup',
 'supervisor.tailProcessLog',
 'supervisor.tailProcessStderrLog',
 'supervisor.tailProcessStdoutLog',
 'system.listMethods',
 'system.methodHelp',
 'system.methodSignature',
 'system.multicall']

"""

class SupervisorAPI(object):
    """
    Laisser cette class autonome pour utilisation en ligne
    
    TODO: faire un contextmanager ou autre pour appeller dans un timeout ou remplacer transport ou proxy
    
    
    """
    
    def __init__(self, serverurl='unix:///tmp/supervisor.sock', 
                 username='radicalspam', password='radicalspam'):
        
        self.serverurl = serverurl
        self.username = username
        self.password = password
        
    def getServerProxy(self):
        """
        TODO: renvoyer que getattr(proxy, 'supervisor')
        """
        
        return xmlrpclib.Server('http://localhost:9001/RPC2')
        
        """
        return xmlrpclib.ServerProxy(
            'http://127.0.0.1',
            #transport = SupervisorTransport(username=self.username, password=self.password, serverurl=self.serverurl)
            )
        """
    
    server = property(fget=getServerProxy)
    
    def read_log(self, offset=0, length=8196):
        """
        server.supervisor.readLog(0,100)
        '2012-03-22 06:24:46,372 CRIT Supervisor running as root (no user in config file)\n2012-03-22 06:24:46'
        """
        return self.server.supervisor.readLog(offset, length)

    def server_infos(self):
        infos = {}
        infos['api_version'] = self.server.supervisor.getAPIVersion()
        infos['supervisor_version'] = self.server.supervisor.getSupervisorVersion()
        infos['version'] = self.server.supervisor.getVersion()
        infos['id'] = self.server.supervisor.getIdentification()
        infos['state'] = self.server.supervisor.getState()
        """
        multi = xmlrpclib.MultiCall(self.server)
        multi.supervisor.getAPIVersion()
        multi.supervisor.getSupervisorVersion()
        multi.supervisor.getVersion()
        multi.supervisor.getIdentification()
        multi.supervisor.getState()
        results = []
        for r in multi():
            results.append(r)
        print "results : ", results
        infos['api_version'] = results[0]
        infos['supervisor_version'] = results[1]
        infos['version'] = results[2]
        infos['id'] = results[3]
        infos['state'] = results[4]
        print "infos: ", infos
        """
        
        return infos
    
    def all_process_info(self):
        """
        Retourne le getProcessInfo de tous les process gérés par supervisor
        
        Classé par nom de process dans un dict
        """
        results = {}
        infos = self.server.supervisor.getAllProcessInfo()
        for p in infos:
            results[p['name']] = p
        
        return results
    
    def all_config_info(self):
        results = {}
        infos = self.server.supervisor.getAllConfigInfo()
        for p in infos:
            results[p['name']] = p
        return results
    
    def process_info(self, process_name):
        infos = self.server.supervisor.getProcessInfo(process_name)
        infos['is_running'] = True if infos['state'] in RUNNING_STATES else False 
        return infos

    def process_stop(self, process_name, wait=True):
        success = self.server.supervisor.stopProcess(process_name, wait)
        return dict(success=success)
    
    def process_start(self, process_name, wait=True):
        success = self.server.supervisor.startProcess(process_name, wait)
        return dict(success=success)
    
    def process_reload(self, process_name):
        success = self.server.supervisor.signalProcess(process_name, 1) #SIGHUP
        return dict(success=success)
    
    def process_restart(self, process_name, wait=True):
        success = self.server.supervisor.stopProcess(process_name, wait)
        success = self.server.supervisor.startProcess(process_name, wait)
        return dict(success=success)
    
class SupervisorRestAPI(object):
    """
    TODO: mise en cache par un timer
    
    Capturer exception: 
        except xmlrpclib.Fault as err:
            add_log = open(ACTIVITY_LOG, "a")
            add_log.write("%s - %s unsucces restart event %s node's %s process .\n"%( datetime.now().ctime(), session['username'], node_name, process_name ))
            return JsonValue(process_name, node_name, "restart").error(err.faultCode, err.faultString)

    """
    
    def __init__(self, app=None, 
                 url_prefix='/supervisor'):
        
        self.app = None

        self.url_prefix = url_prefix
        
        self._client = None
                
        self._bp = None
        
        if app:
            self.init_app(app)
        
    def init_app(self, app=None):
        
        self.app = app
        
        server_url = self.app.config.get('SUPERVISOR_URL', 'http://127.0.0.1:9001/RPC2') #'unix:///var/run/supervisor.sock')
        
        self._client = SupervisorAPI(serverurl=server_url)#, debug=self.app.debug)
        
        self._create_blueprint()

        #self.app.supervisor_app = self
        
    def get_client(self):
        return self._client
    
    client = property(fget=get_client)
    
    def _create_blueprint(self):
        
        self._bp = Blueprint('supervisor', 
                             __name__, 
                             url_prefix=self.url_prefix,
                             #static_folder='static',
                             #template_folder='templates',
                             )
        self._add_views()
        
        self.app.register_blueprint(self._bp)

    def _add_views(self):
        """
        TODO: stop_all / start_all
        TODO: logs !!!!
        """
    
        @self._bp.route('/help', endpoint='help')
        @self._bp.route('/', endpoint='index')
        @auth.required
        @xmlrpc_error
        def server_index():
            """
            Renvoyer page doc API 
            """
    
        #@cache.cached()
        @self._bp.route('/infos', endpoint='infos')
        @auth.required
        @xmlrpc_error
        def server_infos():
            """
            {
            "api_version": "3.0",
            "id": "supervisor",
            "state": {
                "statecode": 1,
                "statename": "RUNNING"
            },
            "supervisor_version": "4.0.0-dev",
            "version": "3.0"
            }        
            """
            return jsonify(**self.client.server_infos())
    
        #@cache.cached()
        @self._bp.route('/allconfig', endpoint='allconfig')
        @auth.required
        @xmlrpc_error
        def all_config_info():
            return jsonify(**self.client.all_config_info())
        
        #@cache.cached(timeout=5)
        @self._bp.route('/allprocess', endpoint='allprocess')
        @auth.required
        @xmlrpc_error
        def all_process_info():
            #return self.client.all_process_info()
            return jsonify(**self.client.all_process_info())
        
        #@cache.cached(timeout=5)
        @self._bp.route('/process/<string:process_name>', endpoint='process')
        @auth.required
        @xmlrpc_error
        def process_info(process_name):
            """
            TODO: interpréter date
            
            {
                "description": "pid 61, uptime 2:45:13",
                "exitstatus": 0,
                "group": "amavis",
                "logfile": "/var/log/supervisor/amavis.log",
                "name": "amavis",
                "now": 1422472172,
                "pid": 61,
                "spawnerr": "",
                "start": 1422462259,
                "state": 20,
                "statename": "RUNNING",
                "stderr_logfile": "/var/log/supervisor/amavis.log",
                "stdout_logfile": "/var/log/supervisor/amavis.log",
                "stop": 0
                
                "is_running": true,
            }        
            """
            return jsonify(**self.client.process_info(process_name))
    
        @self._bp.route('/process/<string:process_name>/stop/nowait', defaults={'wait': False}, endpoint='process-stop-nowait')
        @self._bp.route('/process/<string:process_name>/stop/wait', defaults={'wait': True}, endpoint='process-stop-wait')
        @self._bp.route('/process/<string:process_name>/stop', defaults={'wait': False}, endpoint='process-stop')
        @auth.required
        @xmlrpc_error
        def process_stop(process_name, wait):
            print("....process_stop wait : ", wait) 
            return jsonify(**self.client.process_stop(process_name, wait=wait))
    
        @self._bp.route('/process/<string:process_name>/start/nowait', defaults={'wait': False}, endpoint='process-start-nowait')
        @self._bp.route('/process/<string:process_name>/start/wait', defaults={'wait': True}, endpoint='process-start-wait')
        @self._bp.route('/process/<string:process_name>/start', endpoint='process-start')
        @auth.required
        @xmlrpc_error
        def process_start(process_name, wait):
            """
            Un second start si déjà stated renvoi:
            {
            "faultCode": 60,
            "faultString": "ALREADY_STARTED: amavis",
            "message": "<Fault 60: 'ALREADY_STARTED: amavis'>"
            }        
            """
            return jsonify(**self.client.process_start(process_name, wait=wait))
        
    
