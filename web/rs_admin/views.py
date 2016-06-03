# -*- coding: utf-8 -*-

import time
from pprint import pprint
from collections import OrderedDict

from flask import (Blueprint, 
                   current_app, 
                   request, 
                   render_template,
                   render_template_string, 
                   url_for, 
                   session, 
                   flash, 
                   abort)

from werkzeug.wsgi import wrap_file
from werkzeug.datastructures import MultiDict

from pymongo import ASCENDING, DESCENDING
from bson import ObjectId

def index():
    return render_template("index.html")