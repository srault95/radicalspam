
import json
import logging
import time

from plumbum import local
from decouple import config as config_from_env
from tplconfig.jinja_config import process_file, Fatal
from tplconfig.config_from import Config

RADICALSPAM_CFG = config_from_env('RADICALSPAM_CFG', 
                                  'yaml:///etc/radicalspam/config.yml')
RADICALSPAM_LOG = config_from_env('RADICALSPAM_LOG', 
                                  '/var/log/radicalspam.log')
RADICALSPAM_LOG_ERROR = config_from_env('RADICALSPAM_LOG_ERROR', 
                                  '/var/log/radicalspam.error.log')

SLEEP = config_from_env('RADICALSPAM_WATCH', type=int, default=60)

PREVIOUS_CONFIG = None
CURRENT_CONFIG = None

PREVIOUS_DATA = None
CURRENT_DATA = None

logger = logging.getLogger(__name__)

def load_config():
    global CURRENT_CONFIG

    new_config = Config(config_from=RADICALSPAM_CFG,
                    silent=False, upper_only=False, parse_env=True).items
    
    if not CURRENT_CONFIG:
        CURRENT_CONFIG = new_config
        return True
    
    old_config_str = json.dumps(CURRENT_CONFIG, sort_keys=True)
    new_config_str = json.dumps(new_config, sort_keys=True)
    if old_config_str == new_config_str:
        return False
    
    CURRENT_CONFIG = new_config
    return True

def is_change_dict(old, new):
    old_str = json.dumps(old, sort_keys=True)
    new_str = json.dumps(new, sort_keys=True)
    return old_str != new_str 

def load_data(src):
    global CURRENT_DATA

    new_config = Config(config_from=src,
                    silent=False, upper_only=False, parse_env=True).items
    
    if not CURRENT_DATA:
        CURRENT_DATA = new_config
        return True
    
    old_config_str = json.dumps(CURRENT_DATA, sort_keys=True)
    new_config_str = json.dumps(new_config, sort_keys=True)
    if old_config_str == new_config_str:
        return False
    
    CURRENT_DATA = new_config
    return True


"""

!!! c'est cette source qui peut changer mais doit toujours fournir un dict 
comme résultat

# /etc/rs/data.yml
# /etc/rs/config.yml
# /etc/rs/templates/
    postfix/
        master.tmpl
"""

def _update(config, package, name, data):

    """
    MANQUE les données de config de l'app !!!
    
    config = CURRENT_CONFIG (dict)
    package = postfix
    name = master
    """
    
    package_conf = config['apps'][package][name]
    
    context = {
      "global": CURRENT_DATA, # toutes les données
      "data": data, # contient les données qui ne concerne que le template en cours
      #"fn": {} # fonctions utilitaires
    }
    
    tmpl = package_conf['src']
    output = package_conf['dest']
    check_cmd = package_conf.get('check_cmd')
    reload_cmd = package_conf.get('reload_cmd')
    
    try:
        process_file(templates_package='rs',
                     input_filename=tmpl, 
                     output_filename=output,
                     kwargs=context)
    except (Fatal, IOError) as err:
        logger.error(str(err))

    if reload_cmd:
        cmd = local(reload_cmd)
        cmd(stdout=RADICALSPAM_LOG, stderr=RADICALSPAM_LOG_ERROR)

def update():
    global PREVIOUS_DATA
    if not PREVIOUS_DATA:
        PREVIOUS_DATA = CURRENT_DATA
    
    #_update(config, package, name, data)
    #is_change_dict
    """
    TROP COMPLIQUE de vérifier diff ou il faut faire appel à la command os diff !
        - + diff dans chaque app
        - utiliser un champs version global et 1 par app (incrémenter) ?
    """
    for app, package in CURRENT_CONFIG['apps'].items():
        for name, config in package.items():
            data = CURRENT_DATA['apps'][package][name]
            old_data = PREVIOUS_DATA['apps'][package][name]
            if is_change_dict(old_data, data):
                _update(CURRENT_CONFIG, package, name, data)

def main():
    while True:
        time.sleep(SLEEP)
        load_config()
        is_change = load_data(CURRENT_CONFIG['global']['nodes'][0])
        if is_change:
            update()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        #TODO: autre interrupt
        pass