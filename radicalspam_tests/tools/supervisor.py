#from six.moves import xmlrpc_client as xmlrpclib

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib 

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

class SupervisorAPI(object):
    
    def __init__(self, serverurl='http://localhost:9000/RPC2', 
                 username='', password=''):
        
        self.serverurl = serverurl
        self.username = username
        self.password = password
        
    def getServerProxy(self):
        return xmlrpclib.Server(self.serverurl)
        
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
