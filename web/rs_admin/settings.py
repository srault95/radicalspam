# -*- coding: utf-8 -*-

from decouple import config
gettext = lambda s: s

class Config(object):
    
    BOOTSTRAP_SERVE_LOCAL = True
    
    MONGODB_URL = config('RSADMIN_MONGODB_URL', 'mongodb://localhost/radicalspam')
    
    SECRET_KEY = config('RSADMIN_SECRET_KEY', 'very very secret key key key')
    
    DEBUG = config('RSADMIN_DEBUG', False, cast=bool)
        
    SENTRY_DSN = config('RSADMIN_SENTRY_DSN', None)
    
    #---Flask-Babel
    TIMEZONE = "UTC"#"Europe/Paris" 
    DEFAULT_LANG = "en"
    ACCEPT_LANGUAGES = ['en', 'fr']
    
    ACCEPT_LANGUAGES_CHOICES = (
        ('en', gettext('English')),
        ('fr', gettext('French')),
    )
    
    BABEL_DEFAULT_LOCALE = DEFAULT_LANG
    BABEL_DEFAULT_TIMEZONE = TIMEZONE
    
    #---Flask-Basic-Auth
    BASIC_AUTH_USERNAME = config('RSADMIN_USERNAME', 'admin')
    BASIC_AUTH_PASSWORD = config('RSADMIN_PASSWORD', 'admin')
    BASIC_AUTH_REALM = ''

    MAIL_ADMINS = config('RSADMIN_MAIL_ADMIN', "root@localhost.com")
    
    #---Flask-Mail
    MAIL_SERVER = config('RSADMIN_MAIL_SERVER', "127.0.0.1")
    MAIL_PORT = config('RSADMIN_MAIL_PORT', 25, cast=int)
    MAIL_USE_TLS = config('RSADMIN_MAIL_USE_TLS', False, cast=bool)
    MAIL_USE_SSL = config('RSADMIN_MAIL_USE_SSL', False, cast=bool)
    #MAIL_DEBUG : default app.debug
    MAIL_USERNAME = config('RSADMIN_MAIL_USERNAME', None)
    MAIL_PASSWORD = config('RSADMIN_MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = config('RSADMIN_MAIL_DEFAULT_SENDER', "root@localhost.com")
    MAIL_MAX_EMAILS = None
    #MAIL_SUPPRESS_SEND : default app.testing
    MAIL_ASCII_ATTACHMENTS = False
    
    #---Flask-Assets
    FLASK_ASSETS_USE_CDN = False
    ASSETS_DEBUG = False
    
        
class Prod(Config):
    pass

class Dev(Config):
    
    BOOTSTRAP_USE_MINIFIED = False

    MONGODB_URL = config('RSADMIN_MONGODB_URL', 'mongodb://localhost/radicalspam_dev')

    DEBUG = True

    SECRET_KEY = 'dev_key'
    
    MAIL_DEBUG = True
    
class Test(Config):

    MONGODB_URL = config('RSADMIN_MONGODB_URL', 'mongodb://localhost/radicalspam_test')
    
    COUNTERS_ENABLE = False

    TESTING = True    
    
    SECRET_KEY = 'test_key'
    
    WTF_CSRF_ENABLED = False
    
    PROPAGATE_EXCEPTIONS = True
    
    CACHE_TYPE = "null"
    
    MAIL_SUPPRESS_SEND = True
    

class Custom(Config):
    pass

