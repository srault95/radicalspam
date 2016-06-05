# -*- coding: utf-8 -*-

import logging
import os

from pymongo import ASCENDING, DESCENDING
from pymongo import MongoClient
from pymongo import TEXT
import IPy
from gevent.wsgi import WSGIServer
import arrow

from rs_admin import constants

UPDATE_INDEXES = False

logger = logging.getLogger(__name__)


def get_mongo_url():
    return constants.MONGODB_URL.strip('"')

def get_mongo_client(url=None, connect=False):
    url = url or get_mongo_url()
    client = MongoClient(url, connect=connect, tz_aware=True)
    return client

def get_mongo_db(url=None, **kwargs):
    url = url or get_mongo_url()
    client = get_mongo_client(url, **kwargs)
    return client.get_default_database()

def create_or_update_indexes(db, force_mode=False, background=True):
    """Create or update MongoDB indexes"""
    
    global UPDATE_INDEXES
    
    if not force_mode and UPDATE_INDEXES:
        return

    db[constants.COL_SYSLOG].create_index([
        ("date", DESCENDING)], 
        name="date_idx",
        background=background)

    db[constants.COL_SYSLOG].create_index([
        ("$**", TEXT)], 
        name="full_text",
        #TODO: weights={"MESSAGE": 1, "PROGRAM": 1, "PRIORITY":1}, 
        background=background)
    
    UPDATE_INDEXES = True

def utcnow():
    return arrow.utcnow().datetime

def do_filesizeformat(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    _bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and "KiB" or "kB"),
        (binary and "MiB" or "MB"),
        (binary and "GiB" or "GB"),
        (binary and "TiB" or "TB"),
        (binary and "PiB" or "PB"),
        (binary and "EiB" or "EB"),
        (binary and "ZiB" or "ZB"),
        (binary and "YiB" or "YB")
    ]
    if _bytes == 1:
        return "1 Byte"
    elif _bytes < base:
        return "%d Bytes" % _bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base * base ** (i + 1)
            if _bytes < unit:
                return "%.1f %s" % ((_bytes / unit), prefix)
        return "%.1f %s" % ((_bytes / unit), prefix)


def stats():

    import psutil
    
    pid = os.getpid()
    process = psutil.Process(pid)

    try:
        mem = process.memory_info()
        
        result = {
            'mem_rss': round(mem.rss, 2), #do_filesizeformat(mem.rss),
            'mem_vms': round(mem.vms, 2), #do_filesizeformat(mem.vms),
            'mem_percent': round(process.memory_percent(), 2),
            'cpu_percent': round(process.cpu_percent(None), 2),
            'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            'connections': len(process.connections()),
        }
        return result
        
    except Exception as err:
        logger.error(str(err))
        return {}
        
class SecureWSGIServer(WSGIServer):
    
    def __init__(self, listener, application=None,
                 security_by_host=False, allow_hosts=None,
                 **kwargs):
        WSGIServer.__init__(self, listener, application=application, **kwargs)
        self._security_by_host = security_by_host
        self._allow_hosts = allow_hosts
    
    def handle(self, socket, address):
        if self._security_by_host and not self._security_check(address):                
            socket.close()
            return
        
        WSGIServer.handle(self, socket, address)
        
    def _security_check(self, address):
        """
        fail2ban: 2015-02-21 09:57:05 [5972] [CRITICAL] reject host [127.0.0.1]
        """
                
        if not self._security_by_host:
            return True
        
        if not self._allow_hosts:
            return True
        
        try:
            host = address[0]
            host_ipy = IPy.IP(host)

            for ip in self._allow_hosts:
                
                allow = IPy.IP(ip)
                
                if allow.len() == 1:
                    if ip == host:
                        return True
                else:
                    if host_ipy in allow:
                        return True

            logger.critical("reject host [%s]" % host)
            return False
        
        except Exception as err:
            logger.error(str(err))
        
        return False
        
        
