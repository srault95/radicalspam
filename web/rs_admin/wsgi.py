# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, request, session, render_template, current_app
from decouple import config as config_from_env

from rs_admin import extensions
from rs_admin import constants

def _conf_logging(debug=False, 
                  stdout_enable=True, 
                  syslog_enable=False,
                  prog_name='rs_admin',
                  config_file=None,
                  LEVEL_DEFAULT="INFO"):

    import sys
    import logging.config
    
    if config_file:
        logging.config.fileConfig(config_file, disable_existing_loggers=True)
        return logging.getLogger(prog_name)
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'debug': {
                'format': 'line:%(lineno)d - %(asctime)s %(name)s: [%(levelname)s] - [%(process)d] - [%(module)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '%(asctime)s %(name)s: [%(levelname)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },    
        'handlers': {
            'null': {
                'level':LEVEL_DEFAULT,
                'class':'logging.NullHandler',
            },
            'console':{
                'level':LEVEL_DEFAULT,
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },      
        },
        'loggers': {
            '': {
                'handlers': [],
                'level': LEVEL_DEFAULT,
                'propagate': False,
            },
            prog_name: {
                #'handlers': [],
                'level': LEVEL_DEFAULT,
                'propagate': True,
            },
        },
    }
    
    if sys.platform.startswith("win32"):
        LOGGING['loggers']['']['handlers'] = ['console']

    elif syslog_enable:
        LOGGING['handlers']['syslog'] = {
                'level':'INFO',
                'class':'logging.handlers.SysLogHandler',
                'address' : '/dev/log',
                'facility': 'daemon',
                'formatter': 'simple'    
        }       
        LOGGING['loggers']['']['handlers'].append('syslog')
        
    if stdout_enable:
        if not 'console' in LOGGING['loggers']['']['handlers']:
            LOGGING['loggers']['']['handlers'].append('console')

    '''if handlers is empty'''
    if not LOGGING['loggers']['']['handlers']:
        LOGGING['loggers']['']['handlers'] = ['console']
    
    if debug:
        LOGGING['loggers']['']['level'] = 'DEBUG'
        LOGGING['loggers'][prog_name]['level'] = 'DEBUG'
        for handler in LOGGING['handlers'].keys():
            LOGGING['handlers'][handler]['formatter'] = 'debug'
            LOGGING['handlers'][handler]['level'] = 'DEBUG' 

    #from pprint import pprint as pp 
    #pp(LOGGING)
    #werkzeug = logging.getLogger('werkzeug')
    #werkzeug.handlers = []
             
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger('')
    
    return logger

def _conf_logging_mail(app):
    from logging.handlers import SMTPHandler
    
    ADMIN = app.config.get("MAIL_ADMINS", None)
    if not ADMIN:
        app.logger.error("Emails address for admins are not configured")
        return
        
    ADMINS = ADMIN.split(",")
    """
    mailhost, fromaddr, toaddrs, subject, credentials=None, secure=None, timeout=5.0
    """
    mail_handler = SMTPHandler(app.config.get("MAIL_SERVER"),
                               app.config.get("MAIL_DEFAULT_SENDER"),
                               ADMINS, 
                               'Application Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    
def _conf_logging_errors(app):
    
    def log_exception(sender, exception, **extra):
        sender.logger.error(str(exception))
        
    from flask import got_request_exception
    got_request_exception.connect(log_exception, app)        

def _conf_sentry(app):
    try:
        from raven.contrib.flask import Sentry
        if app.config.get('SENTRY_DSN', None):
            sentry = Sentry(app, logging=True, level=app.logger.level)
    except ImportError:
        pass
    
def _conf_db(app):
    import gridfs
    from rs_admin.utils import get_mongo_db
    from rs_admin.utils import create_or_update_indexes
    app.db = get_mongo_db(app.config.get("MONGODB_URL"), connect=False)
    app.fs = gridfs.GridFS(app.db)
    create_or_update_indexes(app.db)

def _conf_default_views(app):
    
    from rs_admin import views
    views.set_routes(app)

def _conf_ssl(app):
    """
    Dans manager ?
    """
    pass

def _conf_auth(app):
    """
    TODO: github auth
    TODO: pam auth ?
    """
    extensions.auth.init_app(app)
    
    @app.context_processor
    def is_auth():
        def _is_logged():
            if session.get("is_logged"):
                return True
            
            result = extensions.auth.authenticate()
            
            if result:
                session["is_logged"] = True
                return True
        
        return dict(is_logged=_is_logged)        
    
def _conf_mail(app):
    extensions.mail.init_app(app)

def _conf_processors(app):

    @app.context_processor
    def functions():
        def _split(s):
            return s.split()
        return dict(split=_split)

    @app.context_processor
    def server_time():
        import arrow
        return dict(server_time=arrow.utcnow().to('local').format('YYYY-MM-DD HH:mm:ss ZZ'))
    
def _conf_bootstrap(app):
    from flask_bootstrap import Bootstrap
    Bootstrap(app)

def _conf_bp(app):
    """
    from rs_admin import download
    from rs_admin import views
    from rs_admin import admin
    app.register_blueprint(download.bp, url_prefix='/download')    
    app.register_blueprint(views.bp, url_prefix='/views')
    app.register_blueprint(admin.bp, url_prefix='/_cepremap/admin')
    """

def _conf_errors(app):

    from werkzeug import exceptions as ex

    #class DisabledElement(ex.HTTPException):
    #    code = 307
    #    description = 'c'
    #abort.mapping[307] = DisabledElement
    #def disable_error(error):
    #    return 'Disabled element', 307
    #app.error_handler_spec[None][307] = disable_error
        
    #@app.errorhandler(307)
    """
    def disable_error(error):
        is_json = request.args.get('json') or request.is_xhr
        values = dict(error="307 Error", original_error=error, referrer=request.referrer)
        if is_json:
            values['original_error'] = str(values['original_error'])
            return app.jsonify(values), 307
        return render_template('errors/307.html', **values), 307
    app.error_handler_spec[None][307] = disable_error
    """
    
    @app.errorhandler(ex.InternalServerError)
    def error_500(error):
        is_json = request.args.get('json') or request.is_xhr
        values = dict(error="Server Error", original_error=error, referrer=request.referrer)
        if is_json:
            values['original_error'] = str(values['original_error'])
            return app.jsonify(values), 500
        return render_template('errors/500.html', **values), 500
    
    @app.errorhandler(ex.NotFound)
    def not_found_error(error):
        is_json = request.args.get('json') or request.is_xhr
        values = dict(error="404 Error", original_error=error, referrer=request.referrer)
        if is_json:
            values['original_error'] = str(values['original_error'])
            return app.jsonify(values), 404
        return render_template('errors/404.html', **values), 404

def _conf_jsonify(app):

    from rs_admin import json

    def jsonify(obj):
        content = json.dumps(obj)
        return current_app.response_class(content, mimetype='application/json')

    app.jsonify = jsonify
    
def _conf_assets(app):
    from flask_assets import Bundle
    assets = extensions.assets
    #app.debug = True
    assets.init_app(app)
    
    common_css = [
        "local/bootstrap-3.3.6/css/bootstrap.min.css",
        "local/bootstrap-3.3.6/css/bootstrap-theme.min.css",
        "local/font-awesome.min.css",
    ]
    
    common_js = [
        "local/jquery.min.js",
        "local/bootstrap-3.3.6/js/bootstrap.min.js",
        "local/humanize.min.js",
        "local/lodash.min.js",
        "local/spin.min.js",
        "local/jquery.spin.js",
        "local/bootbox.min.js",
        "local/moment.min.js",
        "local/moment-fr.js",
    ]

    table_css = [
        "local/bootstrap-table.min.css",
    ]    
    table_js = [
        "local/bootstrap-table.min.js",
        "local/bootstrap-table-cookie.min.js",
        "local/bootstrap-table-export.min.js",
        "local/bootstrap-table-filter-control.min.js",
        "local/bootstrap-table-filter.min.js",
        "local/bootstrap-table-flat-json.min.js",
        "local/bootstrap-table-mobile.min.js",
        "local/bootstrap-table-natural-sorting.min.js",
        "local/bootstrap-table-toolbar.min.js",
        "local/bootstrap-table-en-US.min.js",
        "local/bootstrap-table-fr-FR.min.js",
    ]
    
    form_css = [
        "local/awesome-bootstrap-checkbox.min.css",
        "local/daterangepicker.min.css",
        "local/formValidation.min.css",
        "local/chosen.min.css",
    ] + table_css

    form_js = [
        "local/daterangepicker.min.js",
        "local/formValidation.min.js",
        "local/formvalidation-bootstrap.min.js",
        "local/formvalidation-fr_FR.min.js",
        "local/chosen.jquery.min.js",
        "local/mustache.min.js",
        #"local/jquery.sparkline.min.js",
        #"local/dygraph-combined.js",
    ] + table_js

    #TODO: export    
    table_export_js = [
        'bootstrap-table/extensions/export/bootstrap-table-export.min.js',    
        'bootstrap-table/extensions/flat-json/bootstrap-table-flat-json.min.js',
        'bootstrap-table/extensions/toolbar/bootstrap-table-toolbar.js',
        'table-export/tableExport.js',
        'table-export/jquery.base64.js',
        'table-export/html2canvas.js',
        'table-export/jspdf/libs/sprintf.js',
        'table-export/jspdf/jspdf.js',
        'table-export/jspdf/libs/base64.js'
    ]
    
    #274Ko
    common_css_bundler = Bundle(*common_css, 
                                filters='cssmin',
                                output='local/common.css'
                                )
    assets.register('common_css', common_css_bundler)
    
    common_js_bundler = Bundle(*common_js,
                               filters='jsmin', 
                               output='local/common.js')
    assets.register('common_js', common_js_bundler)
    
    assets.register('form_css', Bundle(*form_css,
                                       filters='cssmin', 
                                       output='local/form.css'))
    
    assets.register('form_js', Bundle(*form_js, 
                                      filters='jsmin',
                                      output='local/form.js'))

    assets.register('table_css', Bundle(*table_css,
                                       filters='cssmin', 
                                       output='local/table.css'))

    assets.register('table_js', Bundle(*table_js,
                                       filters='jsmin', 
                                       output='local/table.js'))
    
    with app.app_context():
        assets.cache = True #not app.debug
        assets.manifest = 'cache' if not app.debug else False
        assets.debug = False #app.debug
        #print(assets['common_css'].urls())
        
def _conf_babel(app):
    extensions.babel.init_app(app)        
    
def create_app(config='rs_admin.settings.Prod'):
    
    env_config = config_from_env('RSADMIN_SETTINGS', config)
    
    app = Flask(__name__)
    app.config.from_object(env_config)    

    _conf_db(app)

    app.config['LOGGER_NAME'] = 'rs_admin'
    app._logger = _conf_logging(debug=app.debug, prog_name='rs_admin')
    
    if app.config.get("LOGGING_MAIL_ENABLE", False):
        _conf_logging_mail(app)

    _conf_logging_errors(app)    
    
    extensions.moment.init_app(app)
    
    _conf_bootstrap(app)
    
    _conf_sentry(app)
    
    _conf_errors(app)
    
    _conf_jsonify(app)
    
    _conf_default_views(app)
    
    _conf_bp(app)
    
    _conf_processors(app)
    
    _conf_auth(app)
    
    _conf_mail(app)
    
    _conf_assets(app)
    
    _conf_babel(app)
    
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    return app
