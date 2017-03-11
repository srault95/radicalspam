#!/usr/bin/env python

"""
- Pré-configurer RS pour les tests ou s'adapter à la config ?
    - Test de RS en version demo
    - Test de RS en prod !

- Lancer un serveur smtp en tâche de fond
    - recevra les mails sortant par relayhosts ou transport ?
    - comment éviter dépendances: compiler avec pyinstaller ?

- Synthèse de la configuration en cours:
    - Domaines/Emails autorisés
    - mynetworks
    - tags anti spam
    - ....
    
- A bien traiter:
    - L'environnement doit être correctement réinitialiser à chaque test
    - voir 

- Si supervisor:
    - Test XMLRPC des services et leur état !
    
- Lecture logs !!! mail-xx ou syslog ?
    https://github.com/garyelephant/pygrok
    https://github.com/ninech/logstash-patterns/tree/master/patterns.d    

- Autres tests:
    - direct pyclamd
    - direct amavis protocol ?
    
- Tests minimum:
    - Mails entrants / sortant normals
    - Mail entrant avec virus, spam ou banned
        - Détection
        - Header
        - Notification rcpt, sender, admin
        - Quarantine
    - Mail virus ham selon rules spécifiques de correction dans amavis
    - Mail unchecked
    - Mail greylisted:
        - 1ère présentation
        - 2ème avant fin délai
        - Mail whitelisted
    - Mail Dépassement taille
    - Mail client ip en RBL
        - Besoin serveur RBL pour simuler spamhaus
"""

"""
>>> server = xmlrpclib.Server('http://localhost:9000/RPC2')
>>> server.supervisor.getState()
{'statecode': 1, 'statename': 'RUNNING'}

>>> infos = server.supervisor.getAllProcessInfo()

"""

import time
import os
from pathlib import Path
from pprint import pprint
import contextlib
import delegator

from radicalspam_tests.tools import message
from radicalspam_tests.tools import pyclamd
from radicalspam_tests.tools.mailer import SMTPClient
from radicalspam_tests.tools.server import get_free_port, FakeSMTPServer, AsyncorePoller
from radicalspam_tests.tools.supervisor import SupervisorAPI

from radicalspam_tests.tools import resources

EICAR = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
GTUBE = 'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X'

POSTFIX_CHANGES_PARAMS = []

class RadicalSpamTesting(object):
    """
    # without docker:
    
    >>> r = RadicalSpamTesting()
    >>> r.postfix_configure()
    #tests...
    >>> r.postfix_restore()
    
    #with docker:

    >>> r = RadicalSpamTesting(docker_cmd="docker exec -it radicalspam bash -c")
    >>> r.postfix_configure()
    #tests...
    >>> r.postfix_restore()
    
    >>> r = RadicalSpamTesting(docker_cmd="docker exec -it radicalspam bash -c", supervisor_url="http://127.0.0.1:9000/RPC2", postfix_host="127.0.0.1")
    >>> p = r.all_process_info()
    >>> p['postfix']
    {'state': 20, 'logfile': '/var/log/supervisor/postfix.log', 'exitstatus': 0, 'spawnerr': '', 'description': 'pid 14904, uptime 3:57:44', 'statename': 'RUNNING', 'name': 'postfix', 'group': 'postfix', 'start': 1489210210, 'stop': 0, 'stdout_logfile': '/var/log/supervisor/postfix.log', 'pid': 14904, 'stderr_logfile': '', 'now': 1489224474}        
    """
    #$ docker exec -it radicalspam bash -c "postconf -e 'relayhost=[127.0.0.1]:2500'"
    def __init__(self, 
                 docker_cmd=None,       #docker exec -it radicalspam bash -c
                 supervisor_url=None,   #http://localhost:9000/RPC2
                 postfix_host=None,
                 postfix_port=25,
                 ip_xclients=['127.0.0.1'],
                 domains=['example.net'],
                 mynetworks=['127.0.0.1'],
                 root_email="root@example.net"
                 ):
        
        self.docker_cmd = docker_cmd
        self.postfix_host = postfix_host
        self.postfix_port = postfix_port
        self.ip_xclients = ip_xclients
        self.domains = domains
        self.mynetworks = mynetworks
        self.root_email = root_email

        self.supervisor = None
        
        if supervisor_url:
            self.supervisor = SupervisorAPI(serverurl=supervisor_url)
            
        self.fake_host, self.fake_port = get_free_port()
        self.server = FakeSMTPServer((self.fake_host, self.fake_port), None)
        
        self.postconf_backup = {}
        
    def all_process_info(self):
        if self.supervisor:
            return self.supervisor.all_process_info()
        raise Exception("Supervisor not initialized")

    def get_cmd(self, cmd):
        """
        >>> self.get_cmd('postconf -e smtpd_delay_reject=no')
        "postconf -e smtpd_delay_reject=no"
        
        >>> self.docker_cmd('docker exec -it radicalspam bash -c')
        >>> self.get_cmd('postconf -e smtpd_delay_reject=no')
        docker exec -it radicalspam bash -c "postconf -e smtpd_delay_reject=no"
        """
        
        if not self.docker_cmd:
            return cmd
        
        return "%s \"%s\"" % (self.docker_cmd, cmd)
        
    def postconf_set(self, value, restore=False):
        cmd = self.get_cmd('postconf -e %s' % value)
        print(cmd)
        if not restore:
            cmd_split = value.split('=', 1)
            old_value = self.postconf_get(cmd_split[0])
            self.postconf_backup[cmd_split[0]] = old_value
        r = delegator.run(cmd)
        #r = delegator.run('%s -e %s' % (cmd, value))
        if r.return_code != 0:
            raise Exception("ERROR[%s] CODE[%s]" % (r.err, r.return_code))
        return r.return_code

    def postconf_get(self, param):
        cmd = self.get_cmd('postconf -h %s' % param)
        r = delegator.run(cmd)
        return r.out.strip()

    def is_postfix_value(self, param, value):
        #cmd = self.get_cmd('postconf')
        #r = delegator.run('%s -h %s' % (cmd, param))
        #-H que paramètre
        #-h que value
        cmd = self.get_cmd('postconf -h %s' % param)
        print(cmd)
        r = delegator.run(cmd)
        if r.out.strip() == value:
            return True
        else:
            return False
    
    def postfix_configure(self):
        
        #transport_maps = hash:/etc/postfix/local/transport
        self.postconf_set("transport_maps=")
        
        #TODO: option
        self.postconf_set("content_filter=")
        
        if self.is_postfix_value('smtpd_delay_reject', 'yes'):
            self.postconf_set("smtpd_delay_reject=no")
            #r = delegator.run('%s -e "smtpd_delay_reject=no"' % cmd)
            #POSTFIX_CHANGES_PARAMS.append('smtpd_delay_reject')
    
        if self.is_postfix_value('smtpd_delay_open_until_valid_rcpt', 'yes'):
            self.postconf_set("smtpd_delay_open_until_valid_rcpt=no")
            #r = delegator.run('%s -e "smtpd_delay_open_until_valid_rcpt=no"' % cmd)
            POSTFIX_CHANGES_PARAMS.append('smtpd_delay_open_until_valid_rcpt')
        
        self.postconf_set("smtpd_authorized_xclient_hosts=%s" % ",".join(self.ip_xclients))
        #POSTFIX_CHANGES_PARAMS.append('smtpd_authorized_xclient_hosts')
        #r = delegator.run('%s -e "smtpd_authorized_xclient_hosts=%s"' % (cmd, ",".join(ip_xclients)))
        #if r.return_code != 0:
        #    raise Exception("ERROR[%s] CODE[%s]" % (r.err, r.return_code))

        self.postconf_set("relayhost=[%s]:%s" % (self.fake_host, self.fake_port))
        #POSTFIX_CHANGES_PARAMS.append('relayhost')
        
        self.postfix_reload()
        
        #return r.return_code

    def postfix_restore(self):
        #cmd = self.get_cmd('postconf')
        
        for k, v in self.postconf_backup.items():
            print("RESTORE : ", "%s=%s" % (k, v))
            self.postconf_set("%s=%s" % (k, v), restore=True)

        self.postfix_reload()
    
        
        """
        if 'smtpd_delay_reject' in POSTFIX_CHANGES_PARAMS:
            #r = delegator.run('%s -e "smtpd_delay_reject=yes"' % cmd)
            self.postconf_set("smtpd_delay_reject=yes")
    
        if 'smtpd_delay_open_until_valid_rcpt' in POSTFIX_CHANGES_PARAMS:
            #r = delegator.run('%s -e "smtpd_delay_open_until_valid_rcpt=yes"' % cmd)
            self.postconf_set("smtpd_delay_open_until_valid_rcpt=yes")
        
        POSTFIX_CHANGES_PARAMS.clear()
        
        self.postconf_set("smtpd_authorized_xclient_hosts=")
        #r = delegator.run('%s -e "smtpd_authorized_xclient_hosts="' % cmd)
        #if r.return_code != 0:
        #    raise Exception("ERROR[%s] CODE[%s]" % (r.err, r.return_code))
        """
        
    def postfix_reload(self):
        cmd = self.get_cmd('postfix reload')
        r = delegator.run(cmd)
        return r.return_code

    @contextlib.contextmanager
    def start_server(self):
        try:
            self.async_poller = AsyncorePoller()
            self.async_poller.start()
            self.postfix_configure()
            yield self.server
        except:
            raise
        finally:
            self.server.close()
            self.async_poller.stop()
            self.postfix_restore()

    def TODOassertSendResult(self, result):
        self.assertTrue(result["success"], result["error"])
        
        for cmd in ["connect", "ehlo", "mail", "rcpt", "data", "quit"]:
            self.assertTrue(cmd in result)
            
        self.assertEqual(result["connect"]["code"], 220)
        self.assertEqual(result["ehlo"]["code"], 250)
        self.assertEqual(result["mail"]["code"], 250)
        for r in result["rcpt"]:
            self.assertEqual(r["code"], 250)
        self.assertEqual(result["data"]["code"], 250)
        self.assertEqual(result["quit"]["code"], 221)
        
        duration = 0
        for key, field in result.items():
            if key == "rcpt":
                for r in field:
                    duration += r['duration']
            elif isinstance(field, dict) and 'duration' in field:
                duration += field['duration']
        
        self.assertEqual(duration, result["duration"])
            
    def run_all_tests(self):
        with self.start_server() as server:
            self.test_input_normal()
        
    def test_input_normal(self):
        """
    swaks --h-Subject "test mail entrant - NORMAL" \
       -s 127.0.0.1:25 --xclient 'ADDR=1.1.1.1' \ 
       --from sender@example.org --to myuser@radical-spam.com \
       --attach-type text/html --attach /tmp/mail-normal.txt
        """
        client = SMTPClient(host=self.postfix_host, 
                            port=self.postfix_port,
                            xclient_enable=True,
                            debug_level=1)
        
        msg = message.MessageFaker(id="x1",
                           is_out=False, 
                           from_ip="1.1.1.1", #attention rbl 
                           #from_hostname, 
                           #from_heloname, 
                           #enveloppe_sender="sender@external.com", 
                           #enveloppe_recipients=[], 
                           #sender, 
                           #recipients, 
                           #body, 
                           subject="message normal - test 1", 
                           #random_files, 
                           #is_multipart, 
                           #is_bounce, 
                           filter_status=message.FILTER_CLEAN, 
                           #min_size, 
                           #sent_date, 
                           #lang, 
                           #charset, 
                           domains=self.domains, 
                           mynetworks=self.mynetworks
                           ).create_message()
        print("----------------MESSAGE------------------------")
        pprint(msg)
        
        result = client.send(msg)
        print("------------------RESULT-----------------------")
        pprint(result)
        
        print("WAIT....")
        time.sleep(10)
        
        print("--------------RECEIVE MESSAGES-----------------")
        pprint(self.server._messages)
        print("-----------------------------------------------")
        
        #self.assertSendResult(result)
        #self.assertEqual(len(self.server._messages), 1)
        #server_msg = self.server._messages[0]
        #self.assertEqual(server_msg["mailfrom"], msg["from"]) 
        #self.assertEqual(server_msg["rcpttos"], msg["tos"]) 
        

if __name__ == "__main__":
    #r = RadicalSpamTesting(docker_cmd="docker exec -it radicalspam bash -c", supervisor_url="http://127.0.0.1:9000/RPC2", postfix_host="127.0.0.1")
    r = RadicalSpamTesting(supervisor_url="http://127.0.0.1:9000/RPC2", postfix_host="127.0.0.1")
    r.run_all_tests()