# -*- coding: utf-8 -*-

from flask_testing import TestCase as BaseTestCase

from rs_admin.utils import create_or_update_indexes
#from rs_admin import tests_tools as utils

from rs_admin.utils import create_or_update_indexes as local_create_or_update_indexes 

class TestCase(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.db = self.app.db
        self.assertEqual(self.db.name, "radicalspam_test")
        #utils.clean_mongodb(self.db)
        create_or_update_indexes(self.db, force_mode=True)
        local_create_or_update_indexes(self.db, force_mode=True)

    def create_app(self):
        from rs_admin import wsgi
        app = wsgi.create_app('rs_admin.settings.Test')
        return app