# -*- coding: utf-8 -*-

import time
from pprint import pprint
from collections import OrderedDict
import sys

from flask import (Blueprint, 
                   current_app, 
                   request, 
                   render_template,
                   render_template_string, 
                   url_for,
                   redirect, 
                   session, 
                   flash, 
                   abort)

from werkzeug.wsgi import wrap_file
from werkzeug.datastructures import MultiDict

import arrow
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

from rs_admin import json_tools
from rs_admin import constants
from rs_admin import admin_tools

def index():
    return render_template("index.html")

TEST_SERVICES = {'amavis': {'duration': 0,
            'is_error': False,
            'output': 'run: /etc/service/amavis: (pid 27893) 135713s\n',
            'pid': 27893,
            'state': 'DOWN',
            'status_code': 0},
 'clamd': {'duration': 0,
           'is_error': True,
           'output': 'run: /etc/service/clamd: (pid 24408) 917s\n',
           'pid': None,
           'state': 'UNKNOW',
           'status_code': 1},
 'cron': {'duration': 0,
          'is_error': False,
          'output': 'run: /etc/service/cron: (pid 27890) 135713s\n',
          'pid': 27890,
          'state': 'UP',
          'status_code': 0},
 'freshclam': {'duration': 0,
               'is_error': False,
               'output': 'run: /etc/service/freshclam: (pid 27888) 135713s\n',
               'pid': 27888,
               'state': 'UP',
               'status_code': 0},
 'mongodb': {'duration': 0,
             'is_error': False,
             'output': 'run: /etc/service/mongodb: (pid 6851) 19011s\n',
             'pid': 6851,
             'state': 'UP',
             'status_code': 0},
 'postfix': {'duration': 0,
             'is_error': False,
             'output': 'run: /etc/service/postfix: (pid 27894) 135713s\n',
             'pid': 27894,
             'state': 'UP',
             'status_code': 0},
 'postgrey': {'duration': 0,
              'is_error': False,
              'output': 'run: /etc/service/postgrey: (pid 31798) 132682s\n',
              'pid': 31798,
              'state': 'UP',
              'status_code': 0},
 'redis': {'duration': 0,
           'is_error': False,
           'output': 'run: /etc/service/redis: (pid 27898) 135713s\n',
           'pid': 27898,
           'state': 'UP',
           'status_code': 0},
 'spamd': {'duration': 0,
           'is_error': False,
           'output': 'run: /etc/service/spamd: (pid 27892) 135713s\n',
           'pid': 27892,
           'state': 'UP',
           'status_code': 0}}

def view_services_status():
    if sys.platform in ["win32"]:
        services = TEST_SERVICES
    else:
        services = admin_tools.service_status()
           
    return render_template("services.html", services=services)

def view_services_start(service):
    status = admin_tools.service_start(service)
    #TODO: flash
    return redirect(url_for(".services-status"))

def view_services_reload(service):
    status = admin_tools.service_reload(service)
    #TODO: flash    
    return redirect(url_for(".services-status"))

def view_services_stop(service):
    status = admin_tools.service_stop(service)
    #TODO: flash
    return redirect(url_for(".services-status"))

def view_logs_search():
    """
    TODO: mongo tailable + socket.io
    
    {
        "_id" : ObjectId("57533f38b73e5c224c000003"),
        "seqnum" : NumberLong(3),
        "program" : "mongod.27017",
        "priority" : "info",
        "pid" : NumberLong(6851),
        "message" : "[initandlisten] connection accepted from 127.0.0.1:47021 #61 (4 connections now open)",
        "facility" : "user",
        "date" : ISODate("2016-06-04T20:51:04Z")
    }    
    """
    is_ajax = request.args.get('json') or request.is_xhr
    if not is_ajax:
        return render_template("logs-search.html")
    
    field_src = request.args

    """    
    if request.method == "POST":
        field_src = request.form
    """

    search = field_src.get('search')
    limit = field_src.get('limit', default=100, type=int)
    startDate = arrow.get(field_src.get('startDate')).floor('day').datetime
    endDate = arrow.get(field_src.get('endDate')).ceil('day').datetime
    
    projection = {}
    query = {}
    projection['score'] = {'$meta': 'textScore'}
    query["date"] = {"$gte": startDate, "$lte": endDate}
    
    if search:
        query["$text"] = {"$search": search}

    pprint(query)
        
    cursor = current_app.db[constants.COL_SYSLOG].find(query, projection)
    if limit:
        cursor = cursor.limit(limit)
        
    cursor = cursor.sort([('date', DESCENDING), ('score', {'$meta': 'textScore'})])
    count = cursor.count()
    
    rows = [doc for doc in cursor]
    return json_tools.json_response(rows, {"total": count})

def view_logs_delete():
    ids = request.form.getall("_ids")
    print("ids : ", ids)
    #TODO: flash
    flash("Les entrées ont bien été supprimés.")
    return redirect(url_for('logs-search'))

def view_redis_bayes():
    return render_template("redis-bayes.html")

def view_redis_amavislog():
    return render_template("redis-amavislog.html")

def set_routes(app):
    app.add_url_rule('/', 
                     endpoint='home', 
                     view_func=index)
    
    app.add_url_rule('/logs/search', 
                     endpoint='logs-search', 
                     view_func=view_logs_search,
                     methods=['POST', 'GET'])
    
    app.add_url_rule('/logs/search/delete', 
                     endpoint='logs-search-delete', 
                     view_func=view_logs_delete,
                     methods=['POST'])

    app.add_url_rule('/services/status', 
                     endpoint='services-status', 
                     view_func=view_services_status)
    
    app.add_url_rule('/services/<service>/start', 
                     endpoint='services-start', 
                     view_func=view_services_start)

    app.add_url_rule('/services/<service>/stop', 
                     endpoint='services-stop', 
                     view_func=view_services_stop)
