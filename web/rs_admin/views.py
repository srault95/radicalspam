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
#from rs_admin import admin_tools

def index():
    return render_template("index.html")

def view_services_status():
    _services = current_app.supervisor.all_process_info()
    services = {}
    for service, v in _services.items():
        if service in constants.HIDDEN_SERVICES:
            continue
        
        v['start'] = arrow.get(v['start']).datetime
        v['stop'] = arrow.get(v['stop']).datetime
        services[service] = v
                  
    """
    >>> arrow.get(1465769270)
    <Arrow [2016-06-12T22:07:50+00:00]>
    
    TODO: byssh
    if sys.platform in ["win32"]:
        services = TEST_SERVICES
    else:
        services = admin_tools.service_status()
    """           
    return render_template("services.html", services=services)

"""
MANQUE logique pour ordre de démarrage dans les dépendances
- START: coté, préciser la liste des services qui vont êtres lancé avant
- STOP: ceux qui vont être arrêté
    - postfix: aucun
    - clamav: amavis, freshclam?
    - amavis: clamav 

"""

def view_services_start(service):
    result = current_app.supervisor.process_start(service)
    #TODO: flash
    return redirect(url_for(".services-status"))

def view_services_restart(service):
    result = current_app.supervisor.process_restart(service)
    #TODO: flash
    return redirect(url_for(".services-status"))

def view_services_reload(service):
    result = current_app.supervisor.process_reload(service)
    #TODO: flash    
    return redirect(url_for(".services-status"))

def view_services_stop(service):
    result = current_app.supervisor.process_stop(service)
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

    app.add_url_rule('/services/<service>/restart', 
                     endpoint='services-restart', 
                     view_func=view_services_restart)

    app.add_url_rule('/services/<service>/reload', 
                     endpoint='services-reload', 
                     view_func=view_services_reload)
