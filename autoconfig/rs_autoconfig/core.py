# -*- coding: utf-8 -*-

"""
/etc/radicalspam/config.yml
"""
import sys
import os
import time
import logging

from plumbum import local
from decouple import config as config_from_env
from tplconfig.jinja_config import process_file, Fatal
from tplconfig.config_from import Config

from rs_autoconfig import templates

logging.basicConfig(level=logging.INFO)

RADICALSPAM_CFG = config_from_env('RADICALSPAM_CFG', 
                                  'yaml:///etc/radicalspam/config.yml')
RADICALSPAM_LOG = config_from_env('RADICALSPAM_LOG', 
                                  '/var/log/radicalspam.log')
RADICALSPAM_LOG_ERROR = config_from_env('RADICALSPAM_LOG_ERROR', 
                                  '/var/log/radicalspam.error.log')

SLEEP = config_from_env('RADICALSPAM_WATCH', type=int, default=60)
TEMPLATES_PKG = templates.__path__[0]
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
#DLSTATS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "dlstats"))
PREVIOUS_CONFIG = None
CURRENT_CONFIG = None

logger = logging.getLogger('')

CMD_SUPERVISOR = local["supervisorctl", "-c", "/etc/supervisor/supervisord.conf"]

CMD_RESTART_POSTFIX = CMD_SUPERVISOR["restart postfix"]
CMD_POSTFIX_RELOAD = local["postfix", "reload"]
CMD_POSTFIX_POSTMAP = local["postmap"]

def load_config():
    global CURRENT_CONFIG

    new_config = Config(config_from=RADICALSPAM_CFG,
                    silent=False, upper_only=False, parse_env=True).items
    
    if not CURRENT_CONFIG:
        CURRENT_CONFIG = new_config
        return True
    
    if new_config == CURRENT_CONFIG:
        return False
    
    CURRENT_CONFIG = new_config
    return True

"""
    process_file(templates_package='tplconfig.tests.resources.templates_package', 
                 input_filename='config.conf.tpl', 
                 output_fileobj=fileobj, 
                 kwargs=dict(config=config))

"""

class FilePaths:
    
    postfix = {
        'master.cf': '/etc/postfix/master.cf', 
        'main.cf': '/etc/postfix/main.cf', 
        'relays': '/etc/postfix/local/relays',
        'transport': '/etc/postfix/local/transport',
        'mynetwork': '/etc/postfix/local/mynetwork',
    }
    
    clamav = {
        'clamd.conf': '',
        'clamd.conf': '',
    }

def _update_postfix(items):
    is_restart = False
    is_reload = False
    
    if items["master.cf"] is True:
        try:
            process_file(templates_package='rs_autoconfig',
                         input_filename='postfix/master.cf.tpl', 
                         output_filename=FilePaths.postfix["master.cf"],
                         kwargs=CURRENT_CONFIG)
            is_restart = True
        except (Fatal, IOError) as err:
            logger.error(str(err))

    if is_reload and not is_restart:
        CMD_POSTFIX_RELOAD(stdout=RADICALSPAM_LOG, stderr=RADICALSPAM_LOG_ERROR)
    elif is_restart:
        CMD_RESTART_POSTFIX(stdout=RADICALSPAM_LOG, stderr=RADICALSPAM_LOG_ERROR)
    
    
def _changes_postfix():
    """
    renvoyer le nom des fichiers à mettre à jour
    - comparer les paramètres inluant sur template ?
    OU
    - Faire sortie temp et use diff pour vérifier si change ? 
    """    
    return {
        'master.cf': False, 
        'main.cf': False, 
        'relays': False,
        'transport': False,
        'mynetwork': False,
    }

def _is_change(items):
    return True in list(items.values())
    
def update():
    global PREVIOUS_CONFIG
    if not PREVIOUS_CONFIG:
        PREVIOUS_CONFIG = CURRENT_CONFIG
        
    """
    Pas possible de laisser ici la logique qui décidera des fichiers à mettre à jour
    et des services à relancer.
    
    Il faut que ce soit coté app web que des ordres normalisé soit envoyé ou mis dans une 
    queue de tasks (json)
    
    ex: modification du nom de mx
    1. modifie postfix/main.cf
    2. modifie autre ?
    3. reload postfix    
    """
        
    items = _changes_postfix()
    if _is_change(items):
        _update_postfix(items)
        

def main():
    while True:
        time.sleep(SLEEP)
        is_change = load_config()
        if is_change:
            update()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        #TODO: autre interrupt
        pass